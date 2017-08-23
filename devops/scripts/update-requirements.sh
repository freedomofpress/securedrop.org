#!/bin/bash
#
# Compile requirements files

if [ ! -f devops/.venv/bin/activate ]; then virtualenv --no-site-packages devops/.venv; fi
source devops/.venv/bin/activate

pip-compile --output-file requirements.txt requirements.in
pip-compile --output-file dev-requirements.txt dev-requirements.in
