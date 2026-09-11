#!/bin/bash
#
# Restore a database dump for the current git branch.

set -euo pipefail

# Honour the engine chosen by the justfile; fall back to docker standalone.
COMPOSE="${COMPOSE:-docker compose}"

# `/` in a branch name would otherwise become a directory in the dump path.
BRANCH="$(git rev-parse --abbrev-ref HEAD | tr / -)"
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

# Terminate all other connections. The maintenance commands connect over the
# container's unix socket, which the postgres image trusts; `$OWNER` is the
# superuser this compose stack creates.
$COMPOSE exec -T "$CONTAINER" psql -o /dev/null -U "$OWNER" postgres \
    -c "ALTER DATABASE $DBNAME CONNECTION LIMIT 1;"
$COMPOSE exec -T "$CONTAINER" psql -o /dev/null -U "$OWNER" postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DBNAME';"

# `set -e` aborts here if the drop fails, replacing the previous explicit
# `[ $? -ne 0 ] && echo ... && exit 1` guard, which covered only this one command
# and left every other step unchecked.
$COMPOSE exec -T "$CONTAINER" dropdb -U "$OWNER" "$DBNAME"
$COMPOSE exec -T "$CONTAINER" createdb -U "$OWNER" --encoding UTF8 \
    --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --template=template0 \
    --owner "$OWNER" "$DBNAME"
# No `-n public`: this schema depends on the `hstore` extension, and extensions
# carry no schema in the dump's TOC, so a schema filter would drop the
# CREATE EXTENSION the restore then trips over.
$COMPOSE exec -T "$CONTAINER" pg_restore -U "$OWNER" -1 --no-owner \
    --role="$OWNER" --dbname="$DBNAME" < "$FILE"
