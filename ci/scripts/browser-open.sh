#!/bin/bash
#
# Open a web-browser pointing at the dev django web-app,
# using the CLI tooling native to Mac/Linux.

PLATFORM="$(uname -o)"

# Dev only. There was once a `prod` branch here that looked for an nginx
# container on port 8080, but no compose file has defined an nginx service for
# some time, so it could never fire.
COMPOSE="${COMPOSE:-docker compose}"
DJANGO_URL="http://$($COMPOSE -f docker-compose.yaml port django 8000)"
export DJANGO_URL

# Are we on Linux?
if [[ "${PLATFORM}" == *"linux"* ]]; then
    xdg-open "${DJANGO_URL}" &
# I guess we are on Mac :shrug:
else
    open "${DJANGO_URL}" &
fi
