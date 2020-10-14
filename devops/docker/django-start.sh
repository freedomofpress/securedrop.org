#!/bin/bash
# Container entrypoint script for Django applications.
set -e


wait_for_node() {
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        echo "Waiting for node to start..."
        while [ ! -f .node_complete ]
        do
            sleep 2
        done
        rm -v .node_complete
    fi
}

wait_for_postgres() {
    echo "Waiting for postgres to start..."
    until nc -z "${DJANGO_DB_HOST?}" "${DJANGO_DB_PORT?}"
    do
        sleep 2
    done
}

django_start() {
    ./manage.py migrate
    if [ "${DJANGO_COLLECT_STATIC}" == "yes" ]; then
        ./manage.py collectstatic -c --noinput
    fi
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        ./devops/scripts/version-file.sh
        ./manage.py runserver 0.0.0.0:8000
    else
        gunicorn -c /etc/gunicorn/gunicorn.py "${DJANGO_APP_NAME?}.wsgi"
    fi
}

wait_for_postgres
wait_for_node
django_start
