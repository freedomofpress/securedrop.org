.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}

.PHONY: ci-go
ci-go: ## Stands-up a prod like environment under one docker container
	@molecule test -s ci

.PHONY: ci-tests
ci-tests: ## Runs testinfra against a pre-running CI container. Useful for debug
	@molecule verify -s ci

.PHONY: dev-tests
dev-tests: ## Run django tests against developer environment
	docker exec sd_django /bin/bash -c "./manage.py test --noinput -k"

.PHONY: dev-go
dev-go: ## Spin-up developer environment with three docker containers
	./devops/scripts/dev.sh

.PHONY: dev-chownroot
dev-chownroot: ## Chown root owned files caused from previous root-run containers
	sudo find $(DIR) -user root -exec chown -Rv $(WHOAMI):$(WHOAMI) '{}' \;

.PHONY: dev-createdevdata
dev-createdevdata: ## Inject development data into the postgresql database
	docker exec sd_django /bin/bash -c "./manage.py createdevdata"

.PHONY: dev-killapp
dev-killapp: ## Kills all developer containers.
	docker kill sd_node sd_postgresql sd_django

.PHONY: dev-resetapp
dev-resetapp: ## Purges django/node and starts them up. Doesnt touch postgres
	molecule converge -s dev

.PHONY: dev-attach-node
dev-attach-node: ## Provide a read-only terminal to attach to node spin-up
	docker attach --sig-proxy=false sd_node

.PHONY: dev-attach-django
dev-attach-django: ## Provide a read-only terminal to attach to django spin-up
	docker attach --sig-proxy=false sd_django

.PHONY: dev-attach-postgresql
dev-attach-postgresql: ## Provide a read-only terminal to attach to django spin-up
	docker attach --sig-proxy=false sd_postgresql

.PHONY: dev-sass-lint
dev-sass-lint: ## Runs sass-lint utility over the code-base
	./devops/scripts/dev-sasslint.sh

.PHONY: dev-import-db
dev-import-db: ## Imports a database dump from file named ./import.db
	docker exec -it sd_postgresql bash -c "cat /django/import.db | sed 's/OWNER\ TO\ [a-z]*/OWNER\ TO\ postgres/g' | psql securedropdb -U postgres &> /dev/null"

.PHONY: dev-save-db
dev-save-db: ## Save a snapshot of the database for the current git branch
	./devops/scripts/savedb.sh

.PHONY: dev-restore-db
dev-restore-db: ## Restore the most recent database snapshot for the current git branch
	./devops/scripts/restoredb.sh


.PHONY: update-pip-dependencies
update-pip-dependencies: ## Uses pip-compile to update requirements.txt
# It is critical that we run pip-compile via the same Python version
# that we're generating requirements for, otherwise the versions may
# be resolved differently.
	docker run -v "$(DIR):/code" -it quay.io/freedomofpress/ci-python \
		bash -c 'pip install pip-tools && \
		pip-compile --no-header --output-file /code/requirements.txt /code/requirements.in && \
		pip-compile --no-header --output-file /code/dev-requirements.txt /code/dev-requirements.in'
# Update the developer-focused reqs for local dev, testing, and CI.
	pip-compile --no-header --output-file devops/requirements.txt devops/requirements.in


.PHONY: flake8
flake8: ## Runs flake8 linting in Python3 container.
	@docker run -v $(PWD):/code -w /code --name fpf_www_flake8 --rm \
		quay.io/freedomofpress/ci-python \
		bash -c "pip install -q flake8 && flake8"

.PHONY: bandit
bandit: ## Runs bandit static code analysis in Python3 container.
	@docker run -it -v $(PWD):/code -w /code --name fpf_www_bandit --rm \
		quay.io/freedomofpress/ci-python \
		bash -c "pip install -q --upgrade bandit && bandit --recursive . -ll --exclude devops,node_modules,molecule,.venv"

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

PHONY: zap
zap: ## Runs the ZAP web application scanning to check the application for vulnerabilities
# or misconfigurations
	docker pull owasp/zap2docker-weekly
	docker run -v $(DIR)/config:/zap/wrk/:ro -t owasp/zap2docker-weekly zap-baseline.py -c zap-baseline.conf -t http://172.17.0.4:8000
	if [ $? -ne 1 ]; then exit 0; else exit 1; fi;
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
