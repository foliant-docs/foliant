#!/bin/bash

# # Write Dockerfile
echo "FROM python:3.9.21-alpine3.20" > Dockerfile
echo "RUN apk add --no-cache --upgrade bash  && \
pip install poetry==1 && \
pip install --no-build-isolation pyyaml==5.4.1" >> Dockerfile

# Run tests in docker
docker build . -t test-foliant:latest

docker run --rm -it -v "./:/app/" -w /app/ test-foliant:latest "./test.sh"

# Remove Dockerfile
rm Dockerfile
