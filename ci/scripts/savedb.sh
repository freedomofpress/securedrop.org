#!/bin/bash
#
# Save a database snapshot for the current git branch.

set -euo pipefail

# Honour the engine chosen by the justfile; fall back to docker standalone.
COMPOSE="${COMPOSE:-docker compose}"

# `/` in a branch name would otherwise become a directory in the dump path.
BRANCH="$(git rev-parse --abbrev-ref HEAD | tr / -)"
DATE="$(date +%Y-%m-%d-%H-%M-%S)"
DUMPFILE="sdo-$BRANCH.$DATE.dump"
DBNAME="securedropdb"
FOLDER="db-snapshots"
OWNER="postgres"

mkdir -p "$FOLDER"

$COMPOSE exec -T postgresql pg_dump -U "$OWNER" --format=custom "$DBNAME" \
    > "$FOLDER/$DUMPFILE"

echo "Saved snapshot: $FOLDER/$DUMPFILE"
