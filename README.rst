.. image:: https://circleci.com/gh/freedomofpress/securedrop.org.svg?style=svg&circle-token=ae1bdad92b508cea5a86c6a84374af0ae3cf9706
    :target: https://circleci.com/gh/freedomofpress/securedrop.org

Development
=============
This README covers how to install and get started with development in this repository. Information for Wagtail editors can be found in the `Wagtail Editors Guide <WAGTAIL.rst>`_.

Table of Contents
-----------------
* `Prerequisites`_
* `Local Development instructions`_
   * `Updating Requirements`_
* `Advanced actions against the database`_
   * `Database import`_
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

* `pipenv <https://docs.pipenv.org/#install-pipenv-today>`_
* `docker <https://docs.docker.com/engine/installation/>`_

Local Development instructions
------------------------------

After both pre-requisite tools are installed. You'll need to setup the
environment. You can do this by entering this directory and typing the following
(should only be a one-time event):


.. code:: bash

    pipenv install
    make dev-init

That will install all the pip dependencies into a local virtualenv and map your
userid to the docker-compose dev env. Anytime in the future you enter this directory
you'll have to re-activate that env by:

.. code:: bash

    pipenv shell
    # or
    pipenv run $command $args

When you want to play with the environment, you will be using
``docker-compose``. Your guide to understand all the nuances of ``docker-compose``
can be found in the `official docs <https://docs.docker.com/compose/reference/>`_. To start the
environment, run the following your first run:

.. code:: bash

    # Starts up the environment
    docker-compose up

    # Inject development data (only needs to be run once)
    make dev-createdevdata

You should be able to hit the web server interface at http://localhost:8000.

Updating Requirements
+++++++++++++++++++++

New requirements should be added to ``*requirements.in`` files, for use with ``pip-compile``.
There are three Python requirements files:

* ``requirements.in`` production application dependencies
* ``dev-requirements.in`` development container additions (e.g. debug toolbar)

Add the desired dependency to the appropriate ``.in`` file, then run:

.. code:: bash

    make update-pip-dependencies

All requirements files will be regenerated based on compatible versions. Multiple ``.in``
files can be merged into a single ``.txt`` file, for use with ``pip``. The Makefile
target handles the merging of multiple files.

The developer environment dependencies are handled via ``pipenv`` and documentation for that
project can be found `here <https://pipenv.readthedocs.io/en/latest/>`_.

Advanced actions against the database
-------------------------------------

Database import
+++++++++++++++

Drop a postgres database dump into the root of the repo and rename it to
``import.db``. To import it into a running dev session (ensure ``docker-compose up`` has
already been started) run ``make dev-import-db``. Note that this will not pull in
images that are referenced from an external site backup.


Connect to postgresql service from host
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

    docker-compose -f prod-docker-compose.yaml

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

Other commands
--------------

In order to ensure that all commands are run in the same environment, we have
added a ``make flake8`` command that runs ``flake8`` in the docker environment,
rather than on your local env.

Management commands
+++++++++++++++++++

Management commands in this repo are modularized. Running ``createdevdata`` will
run all of these commands, but they can also be run indvidually. All commands
listed should be prefaced by ``docker-compose exec django ./manage.py``. Most of
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
