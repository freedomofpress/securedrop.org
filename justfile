# Recipes for developing and testing the securedrop.org website.
# Run `just` (or `just --list`) to see everything available.
#
# Container engine: prefers docker for backwards compat.
# Override explicitly with `CONTAINER_ENGINE=podman just <recipe>`.

engine := env_var_or_default("CONTAINER_ENGINE", "docker")
compose := engine + " compose"
# Must stay in step with PYTHON_IMAGE in ci/containers/Containerfile: pip-compile
# resolves hashes against this interpreter, and the app installs the result. The
# tag alone is not enough -- Docker Hub rebuilds it in place for patches, so
# without the digest the two can silently drift apart.
python_builder := "docker.io/library/python:3.14.6-slim-trixie@sha256:44dd04494ee8f3b538294360e7c4b3acb87c8268e4d0a4828a6500b1eff50061"

# pinning a specific, recent version of pip-tools, so that the dev-env
# reuses the same tooling predictably.
# TODO: drop use of pip-tools in favor of more modern python package management.
pip_tools_version := "7.6.1"
# Directories of hand-authored PNGs safe for automated optimization.
png_paths := "common/static/images/instance-status common/static/images"
# Directories of hand-authored SVGs safe for automated optimization. Excludes
# common/templates/common (Django template tags embedded in <svg> attributes).
svg_paths := "common/static/images/instance-status common/static/images"
# A binary in the bind-mounted node_modules, put there by the `node-modules`
# recipe rather than baked into the image.
svgo := "node_modules/.bin/svgo"
coverage_omit := "'*/migrations/*.py,*/tests/*.py'"

# Show available recipes.
default:
    @just --list

# Write the host UID into .env so containers build/run as your user (see README).
dev-init:
    echo "UID=$(id -u)" > .env

# Same, but non-destructive: every compose invocation interpolates ${UID:?err},
# so recipes depend on this to work from a cold checkout without clobbering an
# .env the developer has added their own variables to.
[private]
env-check:
    [ -f .env ] || echo "UID=$(id -u)" > .env

# node_modules lives in the bind-mounted tree, populated by the `node` service's
# runtime `npm install` -- so a one-shot `compose run` finds it already there,
# unless nothing has populated it yet. The guard is deliberately host-side, and
# skipping the install when the tree is already populated keeps a running
# `just dev` watcher undisturbed.
[private]
node-modules: env-check
    [ -d node_modules ] || {{compose}} run --rm --no-deps node npm ci

# Run the webapp locally, via containers (--build keeps images in sync with the Containerfile).
dev: env-check
    {{compose}} up --build

alias compose := dev

# Build all containers locally.
build: env-check
    {{compose}} build

# The static checks below run with `--no-deps`: their tooling is baked into the
# dev image, so they need neither postgres nor the webpack watcher.
# That keeps them usable without `just dev` running, locally and in CI alike.

# Check Python lint and formatting with ruff, without writing changes.
ruff: env-check
    # TODO: move `ruff` execution to host context; it shouldn't be running in the container
    {{compose}} run --rm -T --no-deps django bash -c "ruff check && ruff format --check"

# Apply ruff's fixes and formatting in place.
ruff-fix: env-check
    {{compose}} run --rm -T --no-deps django bash -c "ruff check --fix && ruff format"

# Static security analysis with bandit.
bandit: env-check
    {{compose}} run --rm -T --no-deps django ./scripts/bandit

# Fail if a model changed without a matching migration.
check-migrations: env-check
    {{compose}} run --rm -T --no-deps django bash -c "./manage.py makemigrations --dry-run --check"

# Fail if a PNG under png_paths could be optimized further by oxipng.
pnglint: env-check
    {{compose}} run --rm -T --no-deps django \
        oxipng -r -o 6 --strip safe {{png_paths}}
    git diff --exit-code -- {{png_paths}}

# Fail if an SVG under svg_paths could be optimized further by svgo.
svglint: node-modules
    {{compose}} run --rm -T --no-deps node \
        {{svgo}} --config=svgo.config.mjs -r {{svg_paths}}
    git diff --exit-code -- {{svg_paths}}

# Lint SASS with stylelint.
stylelint: node-modules
    {{compose}} run --rm --no-deps node npm run stylelint

# Run all project linters.
lint: ruff bandit check-migrations stylelint pnglint svglint

# Run the Django test suite with coverage (fails under 70%).
test:
    {{compose}} exec django bash -ec "\
        coverage run --source='.' ./manage.py test --noinput; \
        coverage html --skip-empty --omit={{coverage_omit}}; \
        coverage report -m --fail-under=70 --skip-empty --omit={{coverage_omit}}"

# Inject development data into the postgresql database.
createdevdata:
    {{compose}} exec django bash -c "./manage.py createdevdata"

# Import a postgres export file located at ./import.db.
import-db:
    {{compose}} exec -T postgresql bash -c "sed 's/OWNER TO [a-z]*/OWNER TO postgres/g' /django/import.db | psql securedropdb -U postgres > /dev/null"

# Save a snapshot of the database for the current git branch.
save-db:
    COMPOSE="{{compose}}" ./ci/scripts/savedb.sh

# Restore the most recent database snapshot for the current git branch.
restore-db:
    COMPOSE="{{compose}}" ./ci/scripts/restoredb.sh

# Recompile prod + dev lockfiles (forward flags, e.g. --upgrade or --upgrade-package=NAME).
pip-compile *FLAGS: (_pip-lock "requirements.txt" "requirements.in" FLAGS) (_pip-lock "dev-requirements.txt" "dev-requirements.in" FLAGS)

# Recompile only the dev lockfile (same flags as pip-compile).
pip-compile-dev *FLAGS: (_pip-lock "dev-requirements.txt" "dev-requirements.in" FLAGS)

# Recompile one lockfile in a clean builder matching the app's Python, so
# hashes resolve identically to production.
# The final chown hands the regenerated lockfile back to whoever owns the input;
# the builder runs as root, so without it a developer is left with root-owned
# requirements files in their checkout.
_pip-lock outfile infile *FLAGS:
    {{engine}} run --rm -v "{{justfile_directory()}}:/code:z" -w /code {{python_builder}} \
        bash -c 'apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
            pip install pip-tools=={{pip_tools_version}} && \
            pip-compile --generate-hashes --no-header --allow-unsafe {{FLAGS}} \
                --output-file {{outfile}} {{infile}} && \
            chown "$(stat -c "%u:%g" {{infile}})" {{outfile}}'

# The dev image installs the checked-in dev-requirements.txt, so nothing in an
# ordinary build would notice the lockfiles drifting from the .in files.

# Fail if the lockfiles are out of sync with the .in files.
pip-check: pip-compile
    git diff --exit-code -- requirements.txt dev-requirements.txt

# Clean out local developer assets.
clean:
    rm -rvf ./node_modules
