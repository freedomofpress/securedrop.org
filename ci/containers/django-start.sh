#!/bin/bash
# Container entrypoint script for Django applications.
set -e


# Wait for node-start.sh to report that node_modules is populated. Bounded, and
# the marker is left in place on purpose: compose's `depends_on: service_healthy`
# is the real cold-start gate, so a `compose restart django` on its own must not
# block forever waiting for a marker no running node service will re-create.
wait_for_node() {
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        echo "Waiting for node to populate node_modules..."
        for _ in $(seq 30); do
            [ -f .node_complete ] && return 0
            sleep 2
        done
        echo "WARNING: .node_complete not seen after 60s; continuing anyway"
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
    # exec so the server is PID 1 and receives SIGTERM directly; without it bash
    # holds PID 1, swallows the signal, and shutdown waits for SIGKILL.
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        ./ci/scripts/version-file.sh || echo "WARNING: version file creation failed"
        exec ./manage.py runserver 0.0.0.0:8000
    else
        exec gunicorn -c /etc/gunicorn/gunicorn.py "${DJANGO_APP_NAME?}.wsgi"
    fi
}

wait_for_postgres
wait_for_node
django_start
