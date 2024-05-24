# FishSense Docker Dev 
This project is to create a docker container that has the development dependencies for running FishSense code.  It is based off of Ubuntu 24.04 and does not currently support CUDA.

## Build Locally
```
docker build . -t ghcr.io/ucsd-e4e/fishsense-docker-dev:main
```