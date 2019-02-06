#!/bin/bash
#
# Enable hstore extension on databases
for databasename in template1 ${POSTGRES_DB}; do
    psql -U "${POSTGRES_USER}" -c "CREATE EXTENSION IF NOT EXISTS hstore" "${databasename}"
done
