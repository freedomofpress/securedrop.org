#!/bin/bash
# Container entrypoint for the dev webpack watcher.
set -e

# node_modules lives in the bind-mounted checkout, not the image, so it has to be
# populated at runtime.
npm install

# Build and watch any develop-pkgs/*/package.json and collect the watch pids
watcher_pids=""
if [ -d ./develop-pkgs ]; then
  for d in ./develop-pkgs/*; do
    if [ -f "${d}/package.json" ]; then
      ( cd "$d" && npm install && npm run start ) &
      watcher_pids="$watcher_pids $!"
    fi
  done
fi

# `.node_complete` is the handshake consumed by django-start.sh's wait_for_node():
# it signals that node_modules is populated, so Django's own tooling can rely on
# the tree being complete. Compose's `depends_on: node: service_healthy` is the
# stronger gate for the bundles themselves.
touch .node_complete

# Watch the main securedrop.org webpack build
npm run start &

# Wait for all the watchers, exiting if any watcher exits.
watcher_pids="$watcher_pids $!"
wait -n $watcher_pids
