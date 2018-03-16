#!/bin/bash
#
#
#


pipenv --python "$(which python)" 2>&1 > /dev/null

find ~/ -type f -name 'python' -exec /sbin/paxctl -cm '{}' \;

export SHELL=/bin/bash
exec /bin/bash -c "$@"
