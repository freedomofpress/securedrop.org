#!/bin/bash
#
# Restore a database dump for the current git branch.

BRANCH=`git rev-parse --abbrev-ref HEAD`
PREFIX="pfi-$BRANCH"
FOLDER="db-snapshots"

FILE=$(find $FOLDER -iname "$PREFIX*.dump" | sort -r | head -n 1)
[ -z $FILE ] && echo "no snapshots found for branch $BRANCH" && exit 1

OWNER="postgres"
DBNAME="securedropdb"
CONTAINER="sd_postgresql"

# Terminate all other connections
docker exec $CONTAINER psql -o /dev/null -h localhost $OWNER postgres -c "ALTER DATABASE $DBNAME CONNECTION LIMIT 1;"
docker exec $CONTAINER psql -o /dev/null -h localhost $OWNER postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DBNAME';"
docker exec $CONTAINER dropdb -U $OWNER $DBNAME
[ $? -ne 0 ] && echo "could not drop database $DBNAME, aborting" && exit 1
docker exec -i $CONTAINER createdb -U $OWNER --encoding UTF8 --lc-collate=en_US.UTF-8 --lc-ctype=en_US.UTF-8 --template=template0 --owner $OWNER $DBNAME
docker exec -i $CONTAINER pg_restore -U $OWNER -1 --no-owner --role=$OWNER -n public --dbname=$DBNAME < "${FILE}"
