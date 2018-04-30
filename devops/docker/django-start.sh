#!/bin/bash
#

wait_for_node() {
    while [ ! -f .node_complete ]
    do
        sleep 2
    done
    rm -v .node_complete
}

psql_hstore_ext() {
    psql -c 'CREATE EXTENSION IF NOT EXISTS hstore;' ${DJANGO_DB_NAME}
    psql -c 'CREATE EXTENSION IF NOT EXISTS hstore;' template1
}

django_start() {
    ./manage.py migrate && ./manage.py runserver 0.0.0.0:8000
}


wait_for_node
psql_hstore_ext
django_start
