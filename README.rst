Development
=============
This README covers how to install and get started with development in this repository. Information for Wagtail editors can be found in the `Wagtail Editors Guide <WAGTAIL.rst>`_.

Table of Contents
-----------------
* Prerequisites_
* `OpenSSL Installation Note`_
* `Local Development instructions`_
   * `Updating Requirements`_
   * `Resetting database`_
   * `Attaching to running containers`_
* `Advanced actions against the database`_
   * `Database import`_
   * `Connect to postgresql service from host`_
   * `Mimic CI and production environment`_
   * `Database snapshots`_
* `Other commands`_
   * `Management commands`_
* `Search`_
   * `Wagtail`_
   * `Documentation`_
   * `Discourse`_


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

Clone the Git repository from ``git@github.com:freedomofpress/securedrop.org.git``.

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
You can also directly access the database (see further below). Note that you'll need
to populate the database with development data using ``make dev-createdevdata``.

Updating Requirements
+++++++++++++++++++++

New requirements should be added to ``*requirements.in`` files, for use with ``pip-compile``.
There are three Python requirements files:

* ``requirements.in`` production application dependencies
* ``dev-requirements.in`` development container additions (e.g. debug toolbar)
* ``deveops/requirements.in`` local testing and CI requirements (e.g. molecule, safety)

Add the desired dependency to the appropriate ``.in`` file, then run:

.. code:: bash

    make update-pip-dependencies

All requirements files will be regenerated based on compatible versions. Multiple ``.in``
files can be merged into a single ``.txt`` file, for use with ``pip``. The Makefile
target handles the merging of multiple files.

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
-------------------------------------

Database import
+++++++++++++++

Drop a postgres database dump into the root of the repo and rename it to
``import.db``. To import it into a running dev session (ensure ``make dev-go`` has
already been started) run ``make dev-import-db``. Note that this will not pull in
images that are referenced from an external site backup.


Connect to postgresql service from host
+++++++++++++++++++++++++++++++++++++++

The postgresql service is exposed to your host on a port that will be displayed
to you in the output of ``make dev-go``. If you have a GUI
database manipulation application you'd like to utilize point it to ``localhost``
with the correct port, username ``securedrop``, password ``securedroppassword``, dbname ``securedropdb``


Mimic CI and production environment
+++++++++++++++++++++++++++++++++++

You can mimic a production environment where django is deployed with gunicorn,
reverse nginx proxy, and debug mode off using the following command:

.. code:: bash

    make ci-go

This is the same command that is run during CI. It is not run using live-code
refresh so it's not a great dev environment but is good for replicating issues
that would come up in production. Note that you'll have to ensure you have the
requirements installed that are in `devops/requirements.txt` or source
`devops/.venv` (if you've already run `make dev-go` at least once).

Database snapshots
++++++++++++++++++

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

Other commands
--------------

In order to ensure that all commands are run in the same environment, we have
added a ``make flake8`` command that runs ``flake8`` in the docker environment,
rather than on your local env.

Management commands
+++++++++++++++++++

Management commands in this repo are modularized. Running ``createdevdata`` will
run all of these commands, but they can also be run indvidually. All commands
listed should be prefaced by ``docker exec sd_django ./manage.py``. Most of
these commands are meant to be used once at the beginning of development.
They should not be run in production as many of them create fake data.


* ``createdevdata [--delete]``
      Runs all of the other management commands and
      creates fake data. The ``delete`` flag deletes the current homepage and
      creates a new one.
* ``createblogdata <number_of_posts>``
    Creates a blog index page and the indicated number of posts.
* ``createdirectory <number_of_instances>``
      Creates a directory page and theindicated number of SecureDrop instances.
* ``createresultgroups [--delete]``
      Creates the initial text for the scan results shown
      on the details page of a securedrop instance. The ``delete`` flag
      removes current result groups and result states.
* ``createfootersettings``
      Creates the initial default text, menus, and buttons for the footer.
* ``createnavmenu [--delete]``
      Creates the main nav menu and links it to the appropriate pages. Creates a
      ``DirectoryPage``, ``BlogIndexPage``, and ``MarketingIndexPage`` if they
      do not yet exist. The ``delete`` flag destroys the existing nav menu.
* ``createsearchmenus [--delete]``
      Creates default search menus. The ``delete`` flag destroys any
      existing search menus.
* ``scan``
      Scan one or all SecureDrop landing pages for security. By default, scans all pages in the directory.

Search
------

Wagtail
+++++++
``get_search_content``
  Method on each page that should return a string of the "searchable content" for that page type. This should generally include HTML-stripped versions of the page body, any tags, anything in the search description field, etc. It's okay for these all to be naively concatenated together. This value is used to provide words to the search engine and is never displayed.

``update_wagtail_index [--rebuild]``
  Crawl Wagtail pages and create ``SearchDocument``s for each one. This command should only be run once when the repo is initialized, as thereafter ``SearchDocument``s will be updated via ``get_search_content`` which is run when pages are created, updated, or deleted. Note that if pages are changed outside of the Wagtail interface, their search documents will not be updated and this command will need to be run again. Pass ``--rebuild`` to this command to delete existing entries for Wagtail pages before fetching new data, which is useful if out-of-date information or pages are in the index.

Documentation
+++++++++++++
``update_docs_index [--rebuild]``
  Crawl the SecureDrop documentation pages on ``https://docs.securedrop.org/en/stable/`` and update the corresponding `SearchDocument` entries.  Pass ``--rebuild`` to this command to delete existing entries for documentation pages before fetching new data, which is useful if out-of-date information or pages are in the index.  Rebuild is usually the behavior that you will want.  Note that this command depends on a particular arrangement and format of HTML and links on the above 3rd party web URL.  If these change in the future, then the command will potentially fail and report zero or only a few documents indexed.

Discourse
+++++++++
``update_discourse_index [--rebuild]``
  Crawl the SecureDrop forum pages on ``https://forum.securedrop.club/`` and update the corresponding ``SearchDocument`` entries.  Pass ``--rebuild`` to this command to delete existing entries for documentation pages before fetching new data, which is useful if out-of-date information or pages are in the index.  Rebuild is usually the behavior that you will want.

Note that this command depends on the Discourse API.  If the API changes in the future, then the command will potentially fail and report zero or only a few documents indexed.  It also means we depend on two settings: ``DISCOURSE_HOST`` which should be set to the name of the Discourse server without the protocol (``forum.securedrop.club``) and ``DISCOURSE_API_KEY``, the value of which must be obtained securely from someone who knows it.  For local development, I recommend placing these settings in ``settings/local.py``.

Authentication and Authorization
--------------------------------

The auth system for SecureDrop admins (not wagtail admins) relies on at least three packages.

 * `django-allauth <http://django-allauth.readthedocs.io/en/latest/index.html>`_ for basic functionality (account management forms, third-party auth providers, email verification, etc.)
* `django-otp <https://django-otp-official.readthedocs.io/>`_ for One Time Password (OTP) functionality, which is the foundation of two-factor authentication (2FA).
* `django-allauth-2fa <https://github.com/percipient/django-allauth-2fa>`_ to link the above two packages together.
