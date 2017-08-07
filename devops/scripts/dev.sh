#!/bin/bash
#
#

# Allow setting Django port to random values by env variable
if [ "${RAND_PORT-false}" != "false" ]; then
    export RAND_PORT=true
fi

if [ ! -f devops/.venv/bin/activate ]; then virtualenv --no-site-packages devops/.venv; fi
source devops/.venv/bin/activate

pip install -U -r devops/requirements.txt > /dev/null

molecule converge -s dev
