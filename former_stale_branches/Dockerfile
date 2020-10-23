
#
# docker build . -t monitoring
# docker run -it -p 8888:8888 -v $(pwd):/home/jupyter/persistent monitoring bash
#


FROM ubuntu:18.04

# Setup host environment.
# Do as privileged root user.

RUN apt-get update --yes \
 && apt-get install --yes --no-install-recommends wget tzdata \
 && rm -rf /var/lib/apt/lists/*


# Install a container init system.
# Sets non-microservice use.

ARG TINI_VERSION=v0.19.0

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini


# Add un-privileged user.

RUN useradd -g users -s /bin/bash --uid 1000 --create-home jupyter


# Install JupyterLab as un-privileged user.

USER jupyter
WORKDIR /home/jupyter

ARG MINICONDA_VERSION=Miniconda3-latest-Linux-x86_64.sh

RUN wget https://repo.anaconda.com/miniconda/${MINICONDA_VERSION} --no-check-certificate --quiet \
 && bash ${MINICONDA_VERSION} -b -p ${HOME}/.miniconda3 \
 && ${HOME}/.miniconda3/bin/conda init bash \
 && ${HOME}/.miniconda3/bin/conda config --set auto_activate_base false \
 && ${HOME}/.miniconda3/bin/conda clean --all --yes \
 && rm -rf ${MINICONDA_VERSION}

ARG CONDA_CONVENIENCE="/home/jupyter/.miniconda3/bin"

RUN PATH="$PATH:$CONDA_CONVENIENCE" \
 && conda install -n base jupyterlab nb_conda_kernels \
 && conda create -n analysis -c conda-forge ipykernel pandas numpy matplotlib pyarrow \
 && conda clean --all --yes


# Add JupyterLab start-up script.

RUN echo '#!/bin/bash' > jupyterlab.sh \
 && echo 'eval "$(conda shell.bash hook)"' >> jupyterlab.sh \
 && echo 'conda activate base &&' >> jupyterlab.sh \
 && echo 'jupyter lab --no-browser --ip=0.0.0.0' >> jupyterlab.sh \
 && chmod +x jupyterlab.sh


# Convenience area.

# Set timezone.
ENV TZ 'Europe/Berlin'

# Add persistent storage mount point.
RUN mkdir persistent

# Set default JupyterLab terminal.
ENV SHELL /bin/bash


# Always enter with init system.

ENTRYPOINT ["/tini", "--"]
