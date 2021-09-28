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

from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


def main():
    setup(
        name='nomad-remote-tools-hub',
        version='0.1.0',
        description='NOMAD remote tools hub allows to run containarized tools remotely',
        author='The NOMAD Authors',
        license='APACHE 2.0',
        packages=find_packages(exclude=['tests', 'tests.*']),
        install_requires=requirements)


if __name__ == '__main__':
    main()