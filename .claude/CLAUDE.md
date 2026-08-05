# SecureDrop Website

## Project Overview

- Django/Wagtail CMS website for SecureDrop
- Python backend, Node.js/Webpack frontend asset bundling
- Docker-based development environment

## Key Paths

- Django project settings: `securedrop/settings/` (base, dev, production, production-ci, production-debug; default is `securedrop.settings.dev`)
- Django apps: `blog/`, `cloudflare/`, `common/`, `directory/`, `forms/`, `github/`, `home/`, `marketing/`, `menus/`, `scanner/`, `search/`, `simple/`, `build/`
- Templates: `securedrop/templates/` (project-level) plus per-app `<app>/templates/` directories
- Frontend source files: `client/` (`common/`, `tor/`, `autocomplete/`)
- Compiled bundles output: `build/static/bundles/`
- Container builds and CI helper scripts: `ci/` (`ci/containers/Containerfile`, `ci/scripts/`)
- Requirements: `requirements.txt`, `dev-requirements.txt` (compiled from `.in` files via pip-compile)

## Tech Stack

- Python 3.14, Django 5.2+, Wagtail 7.4+
- PostgreSQL 14
- Webpack (frontend)
- Ruff (primary linter)

## Development

- `docker compose up` to start services (postgresql, node, django)
- `make dev-init` for initial setup
- Wagtail admin at `/admin` (dev credentials: test/test)
- `make dev-tests` for Django tests
- `make lint`, `make bandit` for code quality
- Main branch: `develop`
- **All Django/Python commands must run inside Docker** via `docker compose exec django ...` (e.g., `docker compose exec django python manage.py makemigrations`). The host machine does not have Django or project dependencies installed.

## Static Files / Frontend Build

- Source JS/SCSS lives in `client/common/js/` and `client/common/sass/`
- Webpack compiles and bundles assets
- Each output bundle requires a separate entry point in `webpack.config.js`
- Current entry points: `common`, `tor`
- Output goes to `build/static/bundles/`; prod files get content hashes
- SCSS is extracted to separate CSS files via MiniCssExtractPlugin
- `webpack-bundle-tracker` writes `webpack-stats.json` for Django integration
- `npm run start` = dev, `npm run build` = production
- Path alias `~` maps to `client/common/js/` for imports

## Testing

- Run the suite with `make dev-tests` (runs `coverage run ... ./manage.py test --noinput` inside the django container, then reports coverage with a 70% floor)
- To run a subset directly: `docker compose exec django ./manage.py test <app or path> --noinput`
