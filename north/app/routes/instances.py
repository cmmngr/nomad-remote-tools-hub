#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from typing import List
from fastapi import APIRouter, HTTPException, Request, Depends
from collections import deque
from datetime import datetime, timedelta
import time
import docker
from docker import DockerClient

from fastapi import APIRouter
from fastapi.params import Depends

from north import config
from north.app.routes.auth import token_launch
from north.app.models import InstanceModel, InstanceResponseModel, ChannelUnavailableError

router = APIRouter()
router_tag = 'instances'


def get_http_date_in(minutes=1) -> str:
    # https://httpwg.org/specs/rfc7231.html#header.date
    return time.strftime(
        '%a, %d %b %Y %H:%M:%S GMT',
        (datetime.utcnow() + timedelta(minutes=minutes))
        .timetuple())


def get_docker_client() -> DockerClient:
    if config.docker_url:
        docker_client = DockerClient(base_url=config.docker_url)
    else:
        docker_client = docker.from_env()

    return docker_client


# Placeholder code for something that retains information of what container channel are available
# Todo: Add channel number tag to the docker container created and use that as a store
available_channel = deque(['0', '1', '2', '3'])


def get_available_channel() -> str:
    try:
        channel = available_channel.popleft()
        return channel
    except IndexError as channel_unavailable:
        raise HTTPException(
            status_code=503,
            detail="channel are currently occupied.",
            headers={"Retry-After": get_http_date_in()}
        ) from channel_unavailable


@router.get(
    '/',
    tags=[router_tag],
    response_model=List[InstanceModel],
    response_model_exclude_unset=True,
    response_model_exclude_none=True)
async def get_instances():
    ''' Get a list of all existing tool instances. '''
    return []


@router.post(
    '/',
    tags=[router_tag],
    response_model=InstanceResponseModel,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    responses={
        200: {
            "description": "Returns the path to the launched instance",
            "content": {
                "application/json": {
                    "example": {"path": "/container/0/"}
                }
            }
        },
        503: {"model": ChannelUnavailableError, "description": "Raises a 503 HTTP error when channels are unavailable"}
    })
async def post_instances(request: Request, instance: InstanceModel, token=Depends(token_launch)):
    ''' Create a new tool instance. '''
    channel = get_available_channel()
    path = f'{request.scope.get("root_path")}/container/{channel}/'
    container_name = f'{config.docker_name_prefix}-{token.token}-{instance.name}'

    docker_client = get_docker_client()

    # Does the user have this service running - Todo: Move to a nice class that handles this in simple funcs
    docker_name_prefix_filter = dict(filters=dict(name=container_name))
    current_containers = docker_client.containers.list(**docker_name_prefix_filter)
    if len(current_containers) != 0:
        path = current_containers[0].labels['path']
        return InstanceResponseModel(path=path)

    docker_client.containers.run(
        image="jupyter/datascience-notebook",
        command=f'start-notebook.sh --NotebookApp.base_url={path}',
        ports={"8888": int(f'1000{channel}')},
        detach=True,
        name=container_name,
        user="1000:1000",
        group_add=["1000"],
        labels={"path": path}
    )

    return InstanceResponseModel(path=path)
