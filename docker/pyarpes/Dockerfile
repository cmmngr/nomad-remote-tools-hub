FROM linuxserver/webtop:ubuntu-openbox

RUN apt update
RUN apt install git pip qt5-default python3-pyqt5 pyqt5-dev-tools cargo -y

RUN pip install --upgrade nodejs
RUN pip install ipywidgets h5glance==0.7 h5grove==0.0.14 \
    jupyterlab[full]==3.2.9 jupyterlab_h5web[full]==1.3.0 \
    punx==0.2.5 nexpy==0.14.1 silx[full]==1.0.0 --prefer-binary
RUN jupyter lab build
RUN jupyter nbextension enable --py widgetsnbextension
RUN jupyter serverextension enable jupyterlab_h5web

RUN pip install git+https://github.com/nomad-coe/nomad-parser-nexus.git@mpes-latest
RUN pip install git+https://github.com/Tommaso-Pincelli/arpes