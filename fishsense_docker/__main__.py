from fishsense_docker.dockerfile import Dockerfile
from argparse import ArgumentParser
from typing import Any

def install_dependencies(dockerfile: Dockerfile, args: Any):
    dockerfile.run("apt-get update && apt-get upgrade -y && \
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
                    && apt-get clean && rm -rf /var/lib/apt/lists/*")
    
    install_nvidia_dependencies(dockerfile, args)


def install_nvidia_dependencies(dockerfile: Dockerfile, args: Any):
    if "nvidia" in args.image:
        dockerfile.run("apt-get update && apt-get install -y kmod \
                            vulkan-tools \
                            clinfo \
                        && apt-get clean && rm -rf /var/lib/apt/lists/*")
        
        dockerfile.arg(NVIDIA_DRIVER_VERSION="560.35.03")
        dockerfile.run("curl https://us.download.nvidia.com/XFree86/Linux-x86_64/560.35.03/NVIDIA-Linux-x86_64-${NVIDIA_DRIVER_VERSION}.run > /driver.run && \
                        chmod +x /driver.run && \
                        /driver.run --no-kernel-modules --no-questions --silent && \
                        rm /driver.run")
        
def configure_user(dockerfile: Dockerfile):
    dockerfile.run("echo 'ubuntu ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers")

    dockerfile.user("ubuntu")
    dockerfile.env(HOME="/home/ubuntu")
    dockerfile.run("mkdir -p ${HOME}")
    dockerfile.workdir("${HOME}")

def install_pyenv(dockerfile: Dockerfile):
    dockerfile.env(PYENV_ROOT="${HOME}/.pyenv", PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}")
    dockerfile.run('git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv && \
                    echo "export PYENV_ROOT=\\"\$HOME/.pyenv\\"" >> ${HOME}/.bashrc && \
                    echo "[[ -d \$PYENV_ROOT/bin ]] && export PATH="\$PYENV_ROOT/bin:\$PATH"" >> ${HOME}/.bashrc && \
                    echo "eval \\"\\$(pyenv init -)\\"" >> ${HOME}/.bashrc && \
                    echo "\\"$(pyenv virtualenv-init -)\\"" >> ${HOME}/.bashrc')
    
    dockerfile.run("pyenv install 3.12 && pyenv global 3.12")
    dockerfile.run("pip install --upgrade pip && \
                    pip install poetry && \
                    pip cache purge")

def main():
    parser = ArgumentParser("fishsense-docker")
    parser.add_argument("-i", "--image", required=True, help="The image for the resulting Dockerfile.")
    parser.add_argument("-o", "--output", required=True, help="The output file for the Dockerfile.")

    args = parser.parse_args()

    dockerfile = Dockerfile(args.image)
    dockerfile.shell("/bin/bash", "-c")

    install_dependencies(dockerfile, args)
    configure_user(dockerfile)

    dockerfile.run("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y")
    install_pyenv(dockerfile)
    
    dockerfile.cmd("/bin/bash")

    with open(args.output, "w") as f:
        f.write(str(dockerfile))

if __name__ == "__main__":
    main()