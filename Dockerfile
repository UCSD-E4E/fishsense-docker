ARG IMAGE="ubuntu:24.04"
FROM ${IMAGE}

SHELL ["/bin/bash", "-c"] 

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y sudo \
                        build-essential \
                        git \
                        libssl-dev \
                        zlib1g-dev \
                        libbz2-dev \
                        libreadline-dev \
                        libsqlite3-dev \
                        wget \
                        curl \
                        llvm \
                        libncurses5-dev \
                        libncursesw5-dev \
                        xz-utils \
                        tk-dev \
                        libffi-dev \
                        liblzma-dev \
                        python3-openssl \
                        libopencv-dev \
                        clang \
                        libclang-dev \
                        llvm \
                        cmake \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ARG BUILD_TYPE=cpu
ARG NVIDIA_DRIVER_VERSION=560.35.03
RUN if [ "${BUILD_TYPE}" = "cuda" ]; then \
    apt-get update && \
    apt-get install -y kmod \
                        vulkan-tools \
                        clinfo \
    && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    curl https://us.download.nvidia.com/XFree86/Linux-x86_64/560.35.03/NVIDIA-Linux-x86_64-${NVIDIA_DRIVER_VERSION}.run > /driver.run && \
                        chmod +x /driver.run && \
                        /driver.run --no-kernel-modules --no-questions --silent && \
                        rm /driver.run \
fi

RUN echo 'ubuntu ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

USER ubuntu
ENV HOME="/home/ubuntu"
RUN mkdir -p ${HOME}
WORKDIR ${HOME}

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv && \
    echo "export PYENV_ROOT=\"\$HOME/.pyenv\"" >> ${HOME}/.bashrc && \
	echo "[[ -d \$PYENV_ROOT/bin ]] && export PATH="\$PYENV_ROOT/bin:\$PATH"" >> ${HOME}/.bashrc && \
	echo "eval \"\$(pyenv init -)\"" >> ${HOME}/.bashrc && \
	echo "\"$(pyenv virtualenv-init -)\"" >> ${HOME}/.bashrc

RUN pyenv install 3.12 && pyenv global 3.12
RUN pip install --upgrade pip && \
    pip install poetry && \
    pip cache purge

CMD ["/bin/bash"]
