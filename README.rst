Development
=============

Prerequisites
-------------

The installation instructions below assume you have the following software on your machine:

* `virtualenv <http://www.virtualenv.org/en/latest/virtualenv.html#installation>`_
* `docker <https://docs.docker.com/engine/installation/>`_
* `openssl <https://www.openssl.org/>`_ (required for ``cryptography``)*

OpenSSL Installation Note
-------------------------

If installing OpenSSL with Homebrew on macOS 10.7+, you will want to set
the following env vars in your shell profile (see this `GitHub comment <https://github.com/pyca/cryptography/issues/2692#issuecomment-272773481>`_):

.. code:: bash

    export LDFLAGS="-L/usr/local/opt/openssl/lib"
    export CPPFLAGS="-I/usr/local/opt/openssl/include"
    export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig"

Local Development instructions
------------------------------

Clone the Git repository from ``git@github.com:littleweaver/securedrop.org.git``.

Run the following commands to get up and running:

.. code:: bash

    make dev-go

or if you want to randomize the django port (to avoid potential port conflict on
your host):

.. code:: bash

    RAND_PORT=yes make dev-go

Whoa? That's it!? Not so fast. It takes a few minutes to kick off (which happens
in the background); in order to monitor progress use the following two commands
(ctrl-c will exit each without killing the container):

.. code:: bash

    make dev-attach-node #attach a shell to the node process
    make dev-attach-django #attach a shell to the python process

You should be able to hit the web server interface at http://localhost:8000.
You can directly access the database on port `15432` (see further below)

Resetting database
++++++++++++++++++

The containers are ephemeral so if you need to reset and start over, kill
the containers and build them back up.

.. code:: bash

    docker rm -f sd_node sd_postgresql sd_django
    make dev-go

If you want to just burn and restart node/django WHILE keeping the postgresql db
intact, you can run:

.. code:: bash
    make dev-killapp
    make dev-go

Attaching to running containers
+++++++++++++++++++++++++++++++

So there are two ways to attach, the first is to attach to an actual running
process using the ``make`` commands listed under installation. The second, is to
connect to a container but land in a shell to run arbitrary commands. The
available containers are - ``django``, ``node``, and ``postgresql``. To connect to one
and get a bash shell (for example the postgresql container):

.. code:: bash

    docker exec -it sd_postgresql bash

Advanced actions against the database
+++++++++++++++++++++++++++++++++++++

Database import
---------------

Drop a postgres database dump into the root of the repo and rename it to
``import.db``. To import it into a running dev session (ensure ``make dev-go`` has
already been started) run ``make dev-import-db``. Note that this will not pull in
images that are referenced from an external site backup.


Connect to postgresql service from host
---------------------------------------

The postgresql service is exposed to your host on port ``15432``. If you have a GUI
database manipulation application you'd like to utilize point it to ``localhost``,
port ``15432``, username ``tracker``, password ``trackerpassword``, dbname ``securedropdb``


Mimic CI and production environment
-----------------------------------

You can mimic a production environment where django is deployment with gunicorn,
reverse nginx proxy, and debug mode off using the following command:

.. code:: bash

    make ci-go

This is the same command that is run during CI. It is not run using live-code
refresh so it's not a great dev environment but is good for replicating issues
that would come up in production. Note that you'll have to ensure you have the
requirements installed that are in `devops/requirements.txt` or source
`devops/.venv` (if you've already run `make dev-go` at least once).

Database snapshots
------------------

When developing, it is often required to switch branches.  These
different branches can have mutually incompatible changes to the
database, which can render the application inoperable.  It is
therefore helpful to be able to easily restore the database to a
known-good state when making experimental changes.  There are two
commands provided to assist in this.

``make dev-save-db``: Saves a snapshot of the current state of the
database to a file in the ``db-snapshots`` folder.  This file is named
for the currently checked-out git branch.

``make dev-restore-db``: Restores the most recent snapshot for the
currently checked-out git branch.  If none can be found, that is,
``make dev-save-db`` has never been run for the current branch, this
command will do nothing.  If a saved database is found, all data in
database will be replaced with that from the file.  Note that this
command will terminate all connections to the database and delete all
data there, so care is encouraged.

Workflow suggestions.  I find it helpful to have one snapshot for each
active branch I'm working on or reviewing, as well as for master.
Checking out a new branch and running its migrations should be
followed by running ``make dev-save-db`` to give you a baseline to
return to when needed.

When checking out a new branch after working on another, it can be
helpful to restore your snapshot from master, so that the migrations
for the new branch, which were presumably based off of master, will
have a clean starting point.
