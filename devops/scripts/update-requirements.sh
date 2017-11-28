#!/bin/bash
#
# Compile requirements files

if [ ! -f devops/.compile-venv/bin/activate ]; then
    virtualenv -p "$(which python3)" --no-site-packages devops/.compile-venv
fi

source devops/.compile-venv/bin/activate
pip install pip-tools safety

pip-compile --output-file requirements.txt requirements.in
pip-compile --output-file dev-requirements.txt dev-requirements.ini
safety check --full-report -r requirements.txt
safety check --full-report -r dev-requirements.txt
