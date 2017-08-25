#!/bin/bash

if [ ! -f devops/.venv/bin/activate ]; then
    echo "virtualenv not found, please run make dev-go"
    exit 1
fi

source devops/.venv/bin/activate
$@
