#!/bin/bash
#
# Restore a database dump for the current git branch.

set -euo pipefail

# Honour the engine chosen by the justfile; fall back to docker standalone.
COMPOSE="${COMPOSE:-docker compose}"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
FOLDER="db-snapshots"
OWNER="postgres"
DBNAME="securedropdb"
CONTAINER="postgresql"

# `sdo-` is the current prefix; `pfi-` is matched too so snapshots taken before
# the rename still restore.
FILE=""
for prefix in "sdo-$BRANCH" "pfi-$BRANCH"; do
    FILE="$(find "$FOLDER" -iname "$prefix*.dump" 2>/dev/null | sort -r | head -n 1)"
    [ -n "$FILE" ] && break
done
if [ -z "$FILE" ]; then
    echo "no snapshots found for branch $BRANCH" >&2
    exit 1
fi
echo "Restoring from: $FILE"

# Terminate all other connections
$COMPOSE exec -T "$CONTAINER" psql -o /dev/null -h localhost "$OWNER" postgres \
    -c "ALTER DATABASE $DBNAME CONNECTION LIMIT 1;"
$COMPOSE exec -T "$CONTAINER" psql -o /dev/null -h localhost "$OWNER" postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DBNAME';"

# `set -e` aborts here if the drop fails, replacing the previous explicit
# `[ $? -ne 0 ] && echo ... && exit 1` guard, which covered only this one command
# and left every other step unchecked.
$COMPOSE exec -T "$CONTAINER" dropdb -U "$OWNER" "$DBNAME"
$COMPOSE exec -T "$CONTAINER" createdb -U "$OWNER" --encoding UTF8 \
    --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --template=template0 \
    --owner "$OWNER" "$DBNAME"
$COMPOSE exec -T "$CONTAINER" pg_restore -U "$OWNER" -1 --no-owner \
    --role="$OWNER" -n public --dbname="$DBNAME" < "$FILE"
