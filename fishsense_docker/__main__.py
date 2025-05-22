from fishsense_docker.dockerfile import Dockerfile
from argparse import ArgumentParser
from typing import Any

def install_dependencies(dockerfile: Dockerfile, args: Any):
    dockerfile.run("apt-get update && apt-get upgrade -y && \
                    apt-get install -y build-essential \
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
                                        libclang-cpp-dev \
                                        llvm-dev \
                                        cmake \
                                        sqlite3 \
                                        vim \
                    && apt-get clean && rm -rf /var/lib/apt/lists/*")
    
    install_nvidia_dependencies(dockerfile, args)


def install_nvidia_dependencies(dockerfile: Dockerfile, args: Any):
    if "nvidia" in args.image:
        dockerfile.run("apt-get update && apt-get install -y ocl-icd-libopencl1 \
                            ocl-icd-opencl-dev \
                            ocl-icd-dev \
                            opencl-headers \
                            clinfo \
                        && apt-get clean && rm -rf /var/lib/apt/lists/*")
        
        dockerfile.run("git clone https://github.com/pocl/pocl.git /pocl \
                       && cd /pocl \
                       && git checkout v6.0 \
                       && mkdir build \
                       && cd build \
                       && cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/ -DENABLE_CUDA=ON .. \
                       && make -j \
                       && make install \
                       && cd / \
                       && rm -rf /pocl")
        
def configure_user(dockerfile: Dockerfile, user: str):
    dockerfile.user(user)
    dockerfile.env(HOME=f"/home/{user}")
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
    
def install_rust(dockerfile: Dockerfile):
    dockerfile.copy("rust-toolchain.toml", "${HOME}/rust-toolchain.toml")
    dockerfile.run("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y")

def main():
    parser = ArgumentParser("fishsense-docker")
    parser.add_argument("-i", "--image", required=True, help="The image for the resulting Dockerfile.")
    parser.add_argument("-u", "--user", required=True, help="The non-root user the container should run under.")
    parser.add_argument("-o", "--output", required=True, help="The output file for the Dockerfile.")

    args = parser.parse_args()

    dockerfile = Dockerfile(args.image)
    dockerfile.shell("/bin/bash", "-c")

    dockerfile.user("root")

    install_dependencies(dockerfile, args)
    configure_user(dockerfile, args.user)

    install_pyenv(dockerfile)
    install_rust(dockerfile)

    dockerfile.run("pip install git+https://github.com/UCSD-E4E/fishsense-lite.git@main")
    
    dockerfile.cmd("/bin/bash")

    with open(args.output, "w") as f:
        f.write(str(dockerfile))

if __name__ == "__main__":
    main()
