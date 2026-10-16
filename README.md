# SecureDrop.org

> [!NOTE]
> By contributing to this project, you agree to abide by our [Code of Conduct](https://github.com/freedomofpress/.github/blob/main/CODE_OF_CONDUCT.md).

This is the code that powers the SecureDrop.org website. It is built with Wagtail and served at [securedrop.org](https://securedrop.org/).

| Environment | Status                                                                                                                           |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Production  | ![Production CI](https://github.com/freedomofpress/securedrop.org/actions/workflows/check.yaml/badge.svg?branch=prod&event=push) |
| Development | ![Develop CI](https://github.com/freedomofpress/securedrop.org/actions/workflows/check.yaml/badge.svg?branch=develop&event=push) |

## Development

### Prerequisites

The installation instructions below assume you have the following
software on your machine:

- [docker](https://docs.docker.com/engine/installation/) or
  [podman](https://podman.io/docs/installation), with "compose"
  support
- [just](https://github.com/casey/just)

### Local Development instructions

When you want to play with the environment, you will be using
`docker compose`. Your guide to understand all the nuances of
`docker compose` can be found in the [official
docs](https://docs.docker.com/compose/reference/). To start the
environment, run the following your first run:

```bash
# Starts up the environment (records your host UID in .env on the way,
# so a bare `docker compose up` works afterwards too)
just dev

# Inject development data (also only needs to be run once)
just createdevdata

# install pre-commit and set up hooks
pip install pre-commit
pre-commit install
```

You should be able to hit the web server interface by running
`just open-browser`:

```bash
just open-browser
```

If have problems starting the application locally, check the
[Troubleshooting](#troubleshooting) section below.

## Testing

### Running the tests

To perform a quick spot check to ensure all tests are passing you can
run:

```bash
just test
```

This runs the Django test suite inside the `django` container with
coverage, and reports a coverage summary (with a 70% floor) when it
finishes.

To quickly run Python linting you can use:

```bash
just lint
```

To run a subset of tests directly:

```bash
docker compose exec django ./manage.py test <app_or_path> --noinput
```

## Troubleshooting

### Database Reset

To reset your database back to its initial state, run:

```bash
just reset-db
```

This removes the postgresql container and re-seeds it by running
`createdevdata`.

### Docker Containers

Sometimes when dependencies are changed or a Docker image needs to be
updated for other reasons, the containers will need to be manually
triggered to rebuild. These commands, listed in order of destructiveness
can resolve most container issues:

```shell
docker compose up --build
```

Adding the `--build` flag tells Docker Compose to detect and update any
images that require new changes. You can safely add the `--build` flag
under most circumstances without adverse effects.

```shell
docker compose up --build --force-recreate
```

Adding the `--force-recreate` flag tells Docker Compose to recreate all
containers that are part of the application. Note that this only
recreates containers from existing images; it does not rebuild the
images themselves, so it won't help if a cached image layer (e.g. a
stale `pip install` or `npm install` step) is the problem.

```shell
docker compose build --no-cache
```

If the above two commands don't help, the build cache itself may be
stale. `--no-cache` throws out Docker's build cache and rebuilds every
image layer from scratch (slow, but thorough). Follow it with
`docker compose up` to start the freshly built images.

If none of the above fix the issues you're encountering, ensure all
docker containers are stopped (`Ctrl-C` if containers are running in a
shell, `docker compose kill` if they are running detached) and run the
following commands. These commands will remove all images and containers
and rebuild from scratch. Any data in your database will be wiped.

```shell
docker compose rm
docker compose up --build
```

### Debugging

If you want to use the [PDB](https://docs.python.org/3/library/pdb.html)
program for debugging, it is possible. First, add this line to an area
of the code you wish to debug:

```python
import ipdb

ipdb.set_trace()
```

Second, attach to the running Django container. This must be done in a
shell, and it is within this attached shell that you will be able to
interact with the debugger. Run:

```bash
just attach
```

Once you have done this, you can load the page that will run the code
with your `import ipdb` and the debugger will activate in the shell you
attached. To detach from the shell without stopping the container press
`Control+P` followed by `Control+Q`.

#### Django Debug Toolbar

For local development, it is possible to enable the [Django Debug
Toolbar](https://django-debug-toolbar.readthedocs.io/en/stable/) by
setting the `ENABLE_DEBUG_TOOLBAR` environment variable when starting
docker compose:

```bash
ENABLE_DEBUG_TOOLBAR=1 docker compose up
```

See the documentation for more information about how to use this tool to
explore template information or SQL queries. Note that when the toolbar
is running, performance of the local server may be affected.

#### Working on dependencies in place

To work on any upstream dependency in-place during development, you can
clone the dependency into the `develop-pkgs/` subdirectory. When you
start the `django` and `node` containers after doing so, a Python
package (providing a `pyproject.toml`) will be installed editable, and
any Node package (providing a `package.json`) will be built and watched,
so they can be worked on in-place while running the full securedrop.org
Django project.

### Mimic production environment

You can mimic a production environment where django is deployed with
gunicorn, a reverse nginx proxy, and debug mode off using the
`prod-docker-compose.yaml` file. Note that build time for this
container takes much longer than the developer environment:

Run it via `just prod`, which builds the image first
(`just build-prod` builds alone):

```bash
just prod
```

All subsequent docker compose commands will need that explicit `-f` flag
pointing to the production-like compose file.

It is not run using live-code refresh, so it's not a great dev
environment but is good for replicating issues that would come up in
production.

## Database management

### Connect to PostgreSQL

To connect to the database, use the following credentials:

- username - `securedrop`
- password - `securedroppassword`
- dbname - `securedropdb`
- the host/port can be determined by running
  `docker compose port postgresql 5432`

### Database import

Drop a Postgres database dump into the root of the repo and rename it to
`import.db`. To import it into a running dev session (ensure
`docker compose up` has already been started) run `just import-db`. Note
that this will not pull in images that are referenced from an external
site backup.

### Database snapshots

When developing, it is often required to switch branches. These
different branches can have mutually incompatible changes to the
database, which can render the application inoperable. It is therefore
helpful to be able to easily restore the database to a known-good state
when making experimental changes. There are two commands provided to
assist in this.

`just save-db`: Saves a snapshot of the current state of the database to
a file in the `db-snapshots` folder. This file is named for the
currently checked-out git branch.

`just restore-db`: Restores the most recent snapshot for the currently
checked-out git branch. If none can be found, that is, `just save-db`
has never been run for the current branch, this command will do nothing.
If a saved database is found, all data in database will be replaced with
that from the file. Note that this command will terminate all
connections to the database and delete all data there, so care is
encouraged.

Workflow suggestions. I find it helpful to have one snapshot for each
active branch I'm working on or reviewing, as well as for master.
Checking out a new branch and running its migrations should be followed
by running `just save-db` to give you a baseline to return to when
needed.

When checking out a new branch after working on another, it can be
helpful to restore your snapshot from master, so that the migrations for
the new branch, which were presumably based off of master, will have a
clean starting point.

## Dependency Management

### Adding new requirements

New requirements should be added to `*requirements.in` files, for use
with `pip-compile`. There are two Python requirements files:

- `requirements.in` production application dependencies
- `dev-requirements.in` local testing and CI requirements

Add the desired dependency to the appropriate `.in` file, then run:

```bash
just pip-compile
```

All requirements files will be regenerated based on compatible versions.
Multiple `.in` files can be merged into a single `.txt` file, for use
with `pip`. The just recipe handles the merging of multiple files.

This process is the same if a requirement needs to be changed (i.e. its
version number restricted) or removed. Make the appropriate change in
the correct `requirements.in` file, then run the above command to
compile the dependencies.

### Upgrading existing requirements

There are separate commands to upgrade a package without changing the
`requirements.in` files. The command

```bash
just pip-compile --upgrade-package=package-name
```

will update the package named `package-name` to the latest version
allowed by the constraints in `requirements.in` and compile a new
`dev-requirements.txt` and `requirements.txt` based on that version.

## Managing CMS Content

You can log in to the Wagtail interface at `/admin` with the following
credentials:

- username - `test`
- password - `test`

## Other Commands

### just

In order to ensure that all commands are run in the same environment, we have added a `just lint` command that checks Python code (`ruff`), SASS (`stylelint`), SVGs (`svgo`), PNGs (`oxipng`). It also runs `bandit` and the migration check. This is done in the container, rather than on your local env.

Use `just ruff-fix` to apply ruff's fixes and formatting in place.

Run `just` on its own to list every available recipe.

### Management Commands

In addition to the management commands provided by [Django](https://docs.djangoproject.com/en/stable/ref/django-admin/) and [Wagtail](http://docs.wagtail.io/en/stable/reference/management_commands.html), the project has a set of its own custom management commands. All commands listed should be prefaced by `docker compose exec django ./manage.py`.

### Dev Data Commands

These commands are meant to be used once at the beginning of
development. They can be run individually or all at once using the
`createdevdata` command. They should not be run in production as they
create fake data.

- `createdevdata [--delete]`

  Runs all of the other `create*` commands and creates fake data. The
  `delete` flag deletes the current homepage and creates a new one.

- `createblogdata <number_of_posts>`

  Creates a blog index page and the indicated number of posts.

- `createdirectory <number_of_instances>`

  Creates a directory page and theindicated number of SecureDrop
  instances.

- `createresultgroups [--delete]`

  Creates the initial text for the scan results shown on the details
  page of a securedrop instance. The `delete` flag removes current
  result groups and result states.

- `createfootersettings`

  Creates the initial default text, menus, and buttons for the footer.

- `createnavmenu [--delete]`

  Creates the main nav menu and links it to the appropriate pages.
  Creates a `DirectoryPage`, `BlogIndexPage`, and `MarketingIndexPage`
  if they do not yet exist. The `delete` flag destroys the existing
  nav menu.

- `createsearchmenus [--delete]`

  Creates default search menus. The `delete` flag destroys any
  existing search menus.

### Scanner Commands

- `scan [securedrops]`

  Scan one or more SecureDrop landing pages (specified by
  space-separated domain names) for security. By default, scans all
  pages in the directory.

### Search Commands

- `update_docs_index [--rebuild]`

  Crawl the SecureDrop documentation pages on
  `https://docs.securedrop.org/en/stable/` and update the
  corresponding `SearchDocument` entries. Pass `--rebuild` to this
  command to delete existing entries for documentation pages before
  fetching new data, which is useful if out-of-date information or
  pages are in the index. Rebuild is usually the behavior that you
  will want. Note that this command depends on a particular
  arrangement and format of HTML and links on the above 3rd party web
  URL. If these change in the future, then the command will
  potentially fail and report zero or only a few documents indexed.

- `update_wagtail_index [--rebuild]`

  Crawl Wagtail pages and create `SearchDocument`s for each one. This
  command should only be run once when the repo is initialized, as
  thereafter `SearchDocument`s will be updated via
  `get_search_content` which is run when pages are created, updated,
  or deleted. Note that if pages are changed outside of the Wagtail
  interface, their search documents will not be updated and this
  command will need to be run again. Pass `--rebuild` to this command
  to delete existing entries for Wagtail pages before fetching new
  data, which is useful if out-of-date information or pages are in the
  index.
