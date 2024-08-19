prefix := /var/www/livedata
app_dir := live_data_server
DJANGO_COMPATIBLE:=$(shell python -c "import django;t=0 if django.VERSION[0]<4 else 1; print(t)")
DJANGO_VERSION:=$(shell python -c "import django;print(django.__version__)")

ifneq ($(shell docker compose version 2>/dev/null),)
  DOCKER_COMPOSE=docker compose
else ifneq ($(shell docker-compose --version 2>/dev/null),)
  DOCKER_COMPOSE=docker-compose
endif


help:
    # this nifty perl one-liner collects all comments headed by the double "#" symbols next to each target and recycles them as comments
	@perl -nle'print $& if m{^[/a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

check:  ## Check dependencies
	@python -c "import django" || echo "\nERROR: Django is not installed: www.djangoproject.com\n"
	@python -c "import psycopg" || echo "\nWARNING: psycopg is not installed: http://initd.org/psycopg\n"
	@python -c "import corsheaders" || echo "\nWARNING: django-cors-headers is not installed: https://github.com/ottoyiu/django-cors-headers\n"

ifeq ($(DJANGO_COMPATIBLE),1)
	@echo "Detected Django $(DJANGO_VERSION)"
else
	$(error Detected Django $(DJANGO_VERSION) < 4. The web monitor requires at least Django 4)
endif

docker/pruneall: docker/compose/validate  ## stop all containers, then remove all containers, images, networks, and volumes
	$(DOCKER_COMPOSE) down --volumes
	docker system prune --all --volumes --force

docker/compose/validate:  ## validate the version of the docker-compose command. Exits quietly if valid.
	@./scripts/docker-compose_validate.sh $(DOCKER_COMPOSE)

docker/compose/local: docker/compose/validate ## compose and start the service locally
	\cp ./deploy-config/docker-compose.envlocal.yml docker-compose.yml
	$(DOCKER_COMPOSE) up --build

.PHONY: clean
clean: ## remove local files from python installation etc.
	rm -f `find . -type f -name '*.py[co]' -o -name '_version.py'` \
	rm -rf `find . -name __pycache__ -o -name "*.egg-info"` \
		.ruff_cache \
		.pytest_cache \
		.coverage htmlcov \
		build dist \
		# docker-compose.yml

.PHONY: check
.PHONY: first_install
.PHONY: help
.PHONY: install
.PHONY: webapp
.PHONY: webapp/core
.PHONY: docker/compose/validate
.PHONY: docker/pruneall
.PHONY: docker/compose/local
