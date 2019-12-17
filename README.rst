SecureDrop.org
==============

.. image:: https://circleci.com/gh/freedomofpress/securedrop.org.svg?style=svg&circle-token=ae1bdad92b508cea5a86c6a84374af0ae3cf9706
    :target: https://circleci.com/gh/freedomofpress/securedrop.org

Table of Contents
-----------------
* `Prerequisites`_
* `Getting Started: The Quick Version`_
* `Getting Started: The Unabridged Edition`_
* `Management Commands`_
* `Dependency Management`_
* `Advanced Actions Against the Database`_
* `Other Commands`_
* `Troubleshooting`_

Prerequisites
-------------

The installation instructions below assume you have the following software on your machine:

* `Docker <https://www.docker.com/get-started>`_
* `Pipenv <https://docs.pipenv.org/#install-pipenv-today>`_ (if not using Docker for Mac)

Getting Started: The Quick Version
----------------------------------

To get started, run:

.. code:: bash

    make dev-init  # one-time command
    docker-compose up  # long-running process to run application server, every time

    # In a separate shell:
    docker-compose exec django ./manage.py createdevdata  # one-time command

Visit ``http://localhost:8000/`` to see the site or ``http://localhost:8000/admin/`` for the Wagtail admin.

Getting Started: The Unabridged Edition
---------------------------------------

The development environment uses Docker Compose to run the application server, database, and webpack compilation processes. If you are using Docker for Mac, this comes preinstalled. You may skip the Pipenv related code. Otherwise, you can install it for this project using Pipenv:

.. code:: bash

    pipenv install

When installed this way, you will need to activate the env before running all ``docker-compose`` commands with:

.. code:: bash

    pipenv shell
    # or
    pipenv run $command $args

These must be run from the project directory.

Before development you *must* run this one-time command.

.. code:: bash

    make dev-init

To start the environment, run the following your first run:

.. code:: bash

    docker-compose up

This is how you start the server every time you are working on the project. This will start a long-running process. You can exit this process with ``ctl-c``. You may wish to open a second shell to run one-off commands while the server is running.

To populate the project with data suitable for development and testing.

.. code:: bash

    docker-compose exec django ./manage.py createdevdata

.. important:: Though your database will persist between *most* runs, it is recommended that you consider it ephemeral and do not use it to store data you don't wish to lose.

You should be able to hit the web server interface at ``http://localhost:8000/``. You can access the Wagtail admin at ``http://localhost:8000/admin/``.

To learn more about Docker Compose, see the `docker-compose CLI docs <https://docs.docker.com/compose/reference/overview/>`_

Management Commands
-------------------

In addition to the management commands provided by `Django <https://docs.djangoproject.com/en/stable/ref/django-admin/>`_ and `Wagtail <http://docs.wagtail.io/en/stable/reference/management_commands.html>`_, the project has a set of its own custom management commands. All commands listed should be prefaced by ``docker-compose exec django ./manage.py``.

Dev Data Commands
+++++++++++++++++

These commands are meant to be used once at the beginning of development.
They can be run individually or all at once using the ``createdevdata`` command.
They should not be run in production as they create fake data.

* ``createdevdata [--delete]``
      Runs all of the other ``create*`` commands and
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

Scanner Commands
++++++++++++++++

* ``scan [securedrops]``
      Scan one or more SecureDrop landing pages (specified by space-separated domain names) for security. By default, scans all pages in the directory.

Search Commands
+++++++++++++++

* ``update_docs_index [--rebuild]``
    Crawl the SecureDrop documentation pages on ``https://docs.securedrop.org/en/stable/`` and update the corresponding ``SearchDocument`` entries.  Pass ``--rebuild`` to this command to delete existing entries for documentation pages before fetching new data, which is useful if out-of-date information or pages are in the index.  Rebuild is usually the behavior that you will want.  Note that this command depends on a particular arrangement and format of HTML and links on the above 3rd party web URL.  If these change in the future, then the command will potentially fail and report zero or only a few documents indexed.
* ``update_wagtail_index [--rebuild]``
    Crawl Wagtail pages and create ``SearchDocument``\ s for each one. This command should only be run once when the repo is initialized, as thereafter ``SearchDocument``\ s will be updated via ``get_search_content`` which is run when pages are created, updated, or deleted. Note that if pages are changed outside of the Wagtail interface, their search documents will not be updated and this command will need to be run again. Pass ``--rebuild`` to this command to delete existing entries for Wagtail pages before fetching new data, which is useful if out-of-date information or pages are in the index.
* ``update_discourse_index [--rebuild]``
    Crawl the SecureDrop forum pages on ``https://forum.securedrop.club/`` and update the corresponding ``SearchDocument`` entries.  Pass ``--rebuild`` to this command to delete existing entries for documentation pages before fetching new data, which is useful if out-of-date information or pages are in the index.  Rebuild is usually the behavior that you will want.

    This command depends on two settings: ``DISCOURSE_HOST`` which should be set to the name of the Discourse server without the protocol (``forum.securedrop.club``) and ``DISCOURSE_API_KEY``. If you require these for development, acquire them securely from a Discourse forum administrator and stash them in ``securedrop/settings/local.py``.

Dependency Management
---------------------

Adding new requirements
+++++++++++++++++++++++

New requirements should be added to ``*requirements.in`` files, for use with ``pip-compile``.
There are two Python requirements files:

* ``requirements.in`` production application dependencies
* ``dev-requirements.in`` local testing and CI requirements
* ``requirements-github.txt`` contains URLs and commit hashes for GitHub-hosted dependencies.

Add the desired dependency to the appropriate ``.in`` file, then run:

.. code:: bash

    make compile-pip-dependencies

All requirements files will be regenerated based on compatible versions. Multiple ``.in``
files can be merged into a single ``.txt`` file, for use with ``pip``. The Makefile
target handles the merging of multiple files.

This process is the same if a requirement needs to be changed (i.e. its version number restricted) or removed.  Make the appropriate change in the correct ``requirements.in`` file, then run the above command to compile the dependencies.

Upgrading existing requirements
+++++++++++++++++++++++++++++++

There are separate commands to upgrade a package without changing the ``requirements.in`` files.  The command

.. code:: bash

    make upgrade-pip PACKAGE=package-name

will update the package named ``package-name`` to the latest version allowed by the constraints in ``requirements.in`` and compile a new ``dev-requirements.txt`` and ``requirements.txt`` based on that version.

If the package appears only in ``dev-requirements.in``, then you must use this command:

.. code:: bash

    make upgrade-pip-dev PACKAGE=package-name

which will update the package named ``package-name`` to the latest version allowed by the constraints in ``requirements.in`` and compile a new ``dev-requirements.txt``.

Advanced Actions Against the Database
-------------------------------------

Database import
+++++++++++++++

Drop a Postgres database dump into the root of the repo and rename it to
``import.db``. To import it into a running dev session (ensure ``docker-compose up`` has
already been started) run ``make dev-import-db``. Note that this will not pull in
images that are referenced from an external site backup.

Connect to PostgreSQL service from host
+++++++++++++++++++++++++++++++++++++++

The postgresql service is exposed to your host on a port that will be displayed
to you in the output of ``docker-compose port postgresql 5432``. If you have a GUI
database manipulation application you'd like to utilize point it to ``localhost``
with the correct port, username ``securedrop``, password ``securedroppassword``, dbname ``securedropdb``

Mimic production environment
+++++++++++++++++++++++++++++++++++

You can mimic a production environment where django is deployed with gunicorn,
a reverse nginx proxy, and debug mode off using the `ci-docker-compose.yaml` file.
Note that build time for this container takes much longer than the developer environment:

.. code:: bash

    docker-compose -f prod-docker-compose.yaml up

It is not run using live-code refresh so it's not a great dev environment but is good for replicating issues
that would come up in production.

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

Other Commands
--------------

In order to ensure that all commands are run in the same environment, we have
added a ``make flake8`` command that runs ``flake8`` in the docker environment,
rather than on your local env.

Troubleshooting
---------------

Docker Container Woes
+++++++++++++++++++++

Sometimes when dependencies are changed or a Docker image needs to be updated for other reasons, the containers will need to be manually triggered to rebuild. These commands, listed in order of destructiveness can resolve most container issues:

.. code:: shell

    docker-compose up --build

Adding the ``--build`` flag tells Docker Compose to detect and update any images that require new changes. You can safely add the ``--build`` flag under most circumstances without adverse effects.

.. code:: shell

    docker-compose up --build --force-recreate

Adding the ``--force-recreate`` flag tells Docker Compose to recreate all containers that are part of the application.

If neither of the above fix the issues you're encountering, ensure all docker containers are stopped (``ctl-c`` if containers are running in a shell, ``docker-compose kill`` if they are running detached) and run the following commands. These commands will remove all images ad containers and rebuild from scratch. Any data in your database will be wiped.

.. code:: shell

    docker-compose rm
    docker-compose up --build


Debugging
+++++++++

If you want to use the `PDB <https://docs.python.org/3/library/pdb.html>`_ program for debugging, it is possible.  First, add this line to an area of the code you wish to debug:

.. code:: python

    import ipdb; ipdb.set_trace()

Second, attach to the running Django container.  This must be done in a shell, and it is within this attached shell that you will be able to interact with the debugger.  The command to attach is ``docker attach <ID_OF_DJANGO_CONTAINER>``, and on UNIX-type systems, you can look up the ID and attach to the container with this single command:

.. code:: bash

    docker attach $(docker-compose ps -q django)

Once you have done this, you can load the page that will run the code with your ``import ipdb`` and the debugger will activate in the shell you attached.  To detach from the shell without stopping the container press ``Control+P`` followed by ``Control+Q``.
