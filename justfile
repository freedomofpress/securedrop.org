# Recipes for developing and testing the securedrop.org website.
# Run `just` (or `just --list`) to see everything available.
#
# Container engine: prefers docker for backwards compat.
# Override explicitly with `CONTAINER_ENGINE=podman just <recipe>`.

engine := env_var_or_default("CONTAINER_ENGINE", "docker")
compose := engine + " compose"
# Locally built from the Containerfile's `lock` stage, which holds both pins the
# resolver needs -- the app's interpreter and Poetry itself -- so there is no
# second copy to keep in step.
lock_image := "localhost/securedroporg-poetry-lock"

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

# Keeps locked versions pyproject.toml still allows; --regenerate starts fresh.

# Re-resolve pyproject.toml into poetry.lock (forward flags, e.g. --regenerate).
lock *FLAGS: (_poetry "lock" FLAGS)

# Raise locked versions within pyproject's constraints (all of them, if unnamed).
lock-upgrade *PACKAGES: (_poetry "update" "--lock" PACKAGES)

# Runs Poetry, then always re-renders the requirements files from poetry.lock.
# Arguments pass via the environment, so shell metacharacters stay inert. The
# image runs as root; chown hands the output back to the checkout's owner.
_poetry +ARGS: _lock-image
    {{engine}} run --rm -v "{{justfile_directory()}}:/code:z" -w /code \
        -e LOCK_ARGS={{quote(ARGS)}} {{lock_image}} \
        bash -ec 'poetry $LOCK_ARGS && \
            poetry export --only=main --output=requirements.txt && \
            poetry export --with=dev --output=dev-requirements.txt && \
            poetry export --only=lock --output=lock-requirements.txt && \
            sed -i "1i # Generated from poetry.lock by just lock -- do not edit." \
                requirements.txt dev-requirements.txt lock-requirements.txt && \
            chown "$(stat -c "%u:%g" justfile)" \
                poetry.lock requirements.txt dev-requirements.txt lock-requirements.txt'

[private]
_lock-image:
    {{engine}} build --quiet --target=lock --file=ci/containers/Containerfile --tag={{lock_image}} .

# Images install the checked-in files, so no ordinary build notices drift.
# `check --lock` verifies the lock's pyproject hash without rewriting it; the
# re-render plus diff catches stale requirements files. Everything goes to
# stderr: CI captures the two streams separately, so a long stdout diff would
# otherwise land after the hint.

# Fail if the generated files are out of sync with pyproject.toml.
lock-check: (_poetry "check" "--lock")
    git diff --exit-code --stat -- poetry.lock requirements.txt dev-requirements.txt lock-requirements.txt >&2 \
        || { echo 'stale: run `just lock` and commit' >&2; exit 1; }

# Clean out local developer assets.
clean:
    rm -rvf ./node_modules
