#!/bin/bash

set -x
cd devops/docker || exit 1

. docker_hashes

if [ $# -ne 1 ]; then
    echo "Provide either 2 or 3 for python ver as arg"
    exit 1
fi

if [ "$1" == "2" ]; then
    docker build --build-arg="HASH=${PYTHON2_HASH}" \
        --build-arg="PY_VER=2" \
        --build-arg="USER=$(id -u)" \
        --build-arg="PIPENV_VER=${PIPENV_VER}" \
        -f ci-pipenv-dockerfile -t fpf.local/pip_env:2 .

elif [ "$1" == "3" ]; then
    docker build --build-arg="HASH=${PYTHON3_HASH}" \
        --build-arg="PY_VER=3" \
        --build-arg="USER=$(id -u)" \
        --build-arg="PIPENV_VER=${PIPENV_VER}" \
        -f ci-pipenv-dockerfile -t fpf.local/pip_env:2 .
if
