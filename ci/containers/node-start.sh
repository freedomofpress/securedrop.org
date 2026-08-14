#!/bin/bash
# Container entrypoint for the dev webpack watcher.
set -e

# node_modules lives in the bind-mounted checkout, not the image, so it has to be
# populated at runtime.
npm install

# `.node_complete` is the handshake consumed by django-start.sh's wait_for_node():
# it signals that node_modules is populated, so Django's own tooling can rely on
# the tree being complete. Compose's `depends_on: node: service_healthy` is the
# stronger gate for the bundles themselves.
touch .node_complete

# exec so webpack is PID 1 and receives SIGTERM directly; without it bash holds
# PID 1, swallows the signal, and `compose down` waits out the grace period.
exec npm run start
