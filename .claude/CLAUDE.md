# SecureDrop Website

## Project Overview

- Django/Wagtail CMS website for SecureDrop
- Python backend, Node.js/Vite frontend asset bundling
- Docker-based development environment

## Key Paths

- Django project settings: `securedrop/settings/` (base, dev, production, production-ci, production-debug; default is `securedrop.settings.dev`)
- Django apps: `blog/`, `cloudflare/`, `common/`, `directory/`, `forms/`, `github/`, `home/`, `marketing/`, `menus/`, `scanner/`, `search/`, `simple/`, `build/`
- Templates: `securedrop/templates/` (project-level) plus per-app `<app>/templates/` directories
- Frontend source files: `client/` (`common/`, `tor/`)
- Compiled bundles output: `build/static/bundles/`
- DevOps/Docker: `devops/`
- Requirements: `requirements.txt`, `dev-requirements.txt` (compiled from `.in` files via pip-compile)

## Tech Stack

- Python 3.14, Django 5.2+, Wagtail 7.4+
- PostgreSQL 14
- Vite (frontend), ESLint + Stylelint (frontend linting), Prettier (JS formatting)
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

- Source JS/Sass lives in `client/common/js/` and `client/common/sass/`
- Vite compiles and bundles assets
- Each output bundle requires a separate entry in `vite.config.js`'s `build.rollupOptions.input`
- Current entry points: `common` (`client/common/js/common.js`), `tor` (`client/tor/js/torEntry.js`)
- Output goes to `build/static/bundles/`; prod files get content hashes
- CSS is extracted automatically for any entry that imports a `.scss`/`.css` file
- `django-vite` reads Vite's `manifest.json` for Django integration (see `DJANGO_VITE` setting)
- `npm run start` = `vite build --watch` (rebuilds on change, no live dev server/HMR), `npm run build` = production
- Path alias `~` maps to `client/common/js/` for imports
- `npm run js-lint` / `npm run style-lint` run ESLint (flat config, `eslint.config.js`) / Stylelint (`stylelint.config.js`)
- `npm run format` / `npm run format-check` run Prettier (`prettier.config.js`) against client JS; `eslint-config-prettier` disables any ESLint stylistic rules that would conflict with it

## Testing

- Run the suite with `make dev-tests` (runs `coverage run ... ./manage.py test --noinput` inside the django container, then reports coverage with a 70% floor)
- To run a subset directly: `docker compose exec django ./manage.py test <app or path> --noinput`
