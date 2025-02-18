# FishSense Docker 
This project ccontains the base docker container for FishSense projects. It currently build three containers
* x86_64 CPU only
* x86_64 CUDA 12.6
* aarch64 CPU only

We have chosen to explicitly not support aarch64+CUDA despite the fact that NVIDIA's CUDA container has support for this. This decision may change in the future if NVIDIA provides additional ARM devices.

## Build Locally (CPU)
```
python -m fishsense_docker --image ubuntu:24.04 --output Dockerfile
dockerfile build -t ghcr.io/ucsd-e4e/fishsense:cpu .
```

## Build Locally (GPU)
```
python -m fishsense_docker --image nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04 --output Dockerfile
dockerfile build -t ghcr.io/ucsd-e4e/fishsense:gpu .
```