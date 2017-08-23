.DEFAULT_GOAL := help
DIR := ${CURDIR}
WHOAMI := ${USER}
RAND_PORT := ${RAND_PORT}

.PHONY: ci-go
ci-go:
	@molecule test -s ci

.PHONY: ci-tests
ci-tests:
	@molecule verify -s ci

.PHONY: dev-go
dev-go:
	./devops/scripts/dev.sh

.PHONY: dev-chownroot
dev-chownroot:
	sudo find $(DIR) -user root -exec chown -Rv $(WHOAMI):$(WHOAMI) '{}' \;

.PHONY: dev-killapp
dev-killapp:
	docker kill sd_node sd_postgresql sd_django

.PHONY: dev-resetapp
dev-resetapp:
	molecule converge -s dev

.PHONY: dev-attach-node
dev-attach-node:
	docker attach --sig-proxy=false sd_node

.PHONY: dev-attach-django
dev-attach-django:
	docker attach --sig-proxy=false sd_django

.PHONY: dev-attach-postgresql
dev-attach-postgresql:
	docker attach --sig-proxy=false sd_postgresql

.PHONY: dev-sass-lint
dev-sass-lint:
	./devops/scripts/dev-sasslint.sh

.PHONY: dev-import-db
dev-import-db:
	docker exec -it sd_postgresql bash -c "cat /django/import.db | sed 's/OWNER\ TO\ [a-z]*/OWNER\ TO\ tracker/g' | psql securedropdb -U tracker &> /dev/null"

.PHONY: ci-devops-builder
ci-devops-builder:
	./devops/scripts/ci-django-build.sh

.PHONY: help
help:
	@cat devops/scripts/help

.PHONY: dev-save-db
dev-save-db:
	./devops/scripts/savedb.sh

.PHONY: dev-restore-db
dev-restore-db:
	./devops/scripts/restoredb.sh

.PHONY: dev-update-requirements
dev-update-requirements:
	./devops/scripts/update-requirements.sh
