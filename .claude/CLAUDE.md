# SecureDrop Website

## Project Overview

- Django/Wagtail CMS website for SecureDrop
- Python backend, Node.js/Webpack frontend asset bundling
- Docker-based development environment

## Key Paths

- Django project settings: `securedrop/settings/` (base, dev, production, testing, local)
- Django apps: `blog/`, `bundles/`, `common/`, `core/`, `home/`, `menus/`, `resources/`, `search/`, `actioncenter/`, `crm/`, `gpg/`, `rate_limiting/`
- Templates: `templates/`
- Static source files: `core/static/` (js, css, fonts, icons, images, logo)
- Compiled bundles output: `core/static/js/bundles/`
- DevOps/Docker: `devops/`
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
- Path alias `~` maps to `core/static/js/` for imports

## Testing

- Django tests: `./manage.py test --settings=securedrop.settings.dev-testing`
- Coverage reporting included in `make dev-tests`
