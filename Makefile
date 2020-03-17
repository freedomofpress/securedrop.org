.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}
UID := $(shell id -u)
GIT_REV := $(shell git rev-parse HEAD | cut -c1-10)
GIT_BR := $(shell git rev-parse --abbrev-ref HEAD)
SD_IMAGE := quay.io/freedomofpress/securedrop.org

.PHONY: dev-init
dev-init: ## Initialize docker environment for developer workflow
	echo UID=$(UID) > .env

.PHONY: check-migrations
check-migrations: ## Check for ungenerated migrations
	docker-compose exec -T django /bin/bash -c "./manage.py makemigrations --dry-run --check"

.PHONY: ci-tests
ci-tests: ## Runs testinfra against a pre-running CI container. Useful for debug
	@molecule verify -s ci

.PHONY: dev-tests
dev-tests: ## Run django tests against developer environment
	docker-compose exec django /bin/bash -c "coverage run --source='.' ./manage.py test --noinput -k; coverage report -m --fail-under=80"

.PHONY: dev-createdevdata
dev-createdevdata: ## Inject development data into the postgresql database
	docker-compose exec django /bin/bash -c "./manage.py createdevdata"

.PHONY: dev-import-db
dev-import-db: ## Imports a database dump from file named ./import.db
	docker-compose exec -it postgresql bash -c "cat /django/import.db | sed 's/OWNER\ TO\ [a-z]*/OWNER\ TO\ postgres/g' | psql securedropdb -U postgres &> /dev/null"

.PHONY: dev-save-db
dev-save-db: ## Save a snapshot of the database for the current git branch
	./devops/scripts/savedb.sh

.PHONY: dev-restore-db
dev-restore-db: ## Restore the most recent database snapshot for the current git branch
	./devops/scripts/restoredb.sh


.PHONY: compile-pip-dependencies
compile-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code -it python:3.5-slim \
		bash -c 'apt-get update && apt-get install gcc -y && \
    pip install --require-hashes -r pip-tools-requirements.txt && \
		pip-compile --generate-hashes --no-header --output-file pip-tools-requirements.txt pip-tools-requirements.in && \
		pip-compile --generate-hashes --no-header --output-file requirements.txt requirements.in && \
		pip-compile --generate-hashes --no-header --allow-unsafe --output-file dev-requirements.txt dev-requirements.in'

.PHONY: upgrade-pip
upgrade-pip: ## Uses pip-compile to update requirements.txt for upgrading a specific package
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code -it python:3.5-slim \
		bash -c 'apt-get update && apt-get install gcc -y && \
    pip install --require-hashes -r pip-tools-requirements.txt && \
		pip-compile --generate-hashes --no-header --upgrade-package $(PACKAGE) --output-file requirements.txt requirements.in && \
		pip-compile --generate-hashes --no-header --allow-unsafe --upgrade-package $(PACKAGE) --output-file dev-requirements.txt dev-requirements.in'


.PHONY: upgrade-pip-dev
upgrade-pip-dev: ## Uses pip-compile to update dev-requirements.txt for upgrading a specific package
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -w /code -it python:3.5-slim \
		bash -c 'apt-get update && apt-get install gcc -y && \
    pip install --require-hashes -r pip-tools-requirements.txt && \
		pip-compile --generate-hashes --no-header --allow-unsafe --upgrade-package $(PACKAGE) --output-file dev-requirements.txt dev-requirements.in'


.PHONY: flake8
flake8: ## Runs flake8 linting in Python3 container.
	@docker-compose run -T django /bin/bash -c "flake8"

.PHONY: bandit
bandit: ## Runs bandit static code analysis in Python3 container.
	@docker run -it -v $(PWD):/code -w /code --name fpf_www_bandit --rm \
		python:3.5-slim \
		bash -c "pip install -q --upgrade bandit && bandit --recursive . -ll --exclude devops,node_modules,molecule,.venv"

.PHONY: npm-audit
npm-audit: ## Checks NodeJS NPM dependencies for vulnerabilities
	@docker-compose run --entrypoint "/bin/ash -c" node 'npm install && $$(npm bin)/npm-audit-plus --ignore 803'

.PHONY: ci-npm-audit
ci-npm-audit:
	@mkdir -p test-results # Creates necessary test-results folder
	@docker-compose run --entrypoint "/bin/ash -c" node 'npm ci && $$(npm bin)/npm-audit-plus --xml --ignore 803 > test-results/audit.xml'

.PHONY: clean
clean: ## clean out local developer assets
	@rm -rvf ./node_modules

.PHONY: safety
safety: ## Runs `safety check` to check python dependencies for vulnerabilities
# Upgrade safety to ensure we are using the latest version.
# Using `--stdin` because `-r` was showing inscrutable errors
	pip install --upgrade safety && \
		for req_file in `find . -type f -name '*requirements.txt'`; do \
			echo "Checking file $$req_file" \
			&& safety check --full-report --stdin < $$req_file \
			&& echo -e '\n' \
			|| exit 1; \
		done

.PHONY: prod-push
prod-push: ## Publishes prod container image to registry
	docker tag $(SD_IMAGE):latest $(SD_IMAGE):$(GIT_REV)-$(GIT_BR)
	docker push $(SD_IMAGE):latest
	docker push $(SD_IMAGE):$(GIT_REV)-$(GIT_BR)

# Explaination of the below shell command should it ever break.
# 1. Set the field separator to ": ##" and any make targets that might appear between : and ##
# 2. Use sed-like syntax to remove the make targets
# 3. Format the split fields into $$1) the target name (in blue) and $$2) the target descrption
# 4. Pass this file as an arg to awk
# 5. Sort it alphabetically
# 6. Format columns with colon as delimiter.
.PHONY: help
help: ## Print this message and exit.
	@printf "Makefile for developing and testing SecureDrop.\n"
	@printf "Subcommands:\n\n"
	@awk 'BEGIN {FS = ":.*?## "} /^[0-9a-zA-Z_-]+:.*?## / {printf "\033[36m%s\033[0m : %s\n", $$1, $$2}' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t
