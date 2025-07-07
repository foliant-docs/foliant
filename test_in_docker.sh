#!/bin/bash


PYTHON_VERSIONS=("3.9" "3.10" "3.11")

for version in "${PYTHON_VERSIONS[@]}"; do
    # Write Dockerfile
    echo "FROM python:${version}-alpine3.20" > Dockerfile
    echo "RUN apk add --no-cache --upgrade bash  && \
    pip install poetry==2.1.1 && \
    apk add git" >> Dockerfile
    echo "RUN git config --global --add safe.directory /app" >> Dockerfile

    # Run tests in docker
    docker build . -t test-foliant:latest

    docker run --rm -it -v "./:/app/" -w /app/ test-foliant:latest "./test.sh"

    # Remove Dockerfile
    rm Dockerfile
done