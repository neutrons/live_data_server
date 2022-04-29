prefix := /var/www/livedata
app_dir := live_data_server
DJANGO_COMPATIBLE:=$(shell python -c "import django;t=0 if django.VERSION[1]<9 else 1; print t")
DJANGO_VERSION:=$(shell python -c "import django;print django.__version__")

# command to run docker compose. change this to be what you have installed
# this can be overriden on the command line
# DOCKER_COMPOSE="docker compose" make startdev
DOCKER_COMPOSE ?= docker-compose

help:
    # this nifty perl one-liner collects all comments headed by the double "#" symbols next to each target and recycles them as comments
	@perl -nle'print $& if m{^[/a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

all:
	@echo "Run make install to install the live data server"

check:  ## Check dependencies
	@python -c "import django" || echo "\nERROR: Django is not installed: www.djangoproject.com\n"
	@python -c "import psycopg2" || echo "\nWARNING: psycopg2 is not installed: http://initd.org/psycopg\n"
	@python -c "import corsheaders" || echo "\nWARNING: django-cors-headers is not installed: https://github.com/ottoyiu/django-cors-headers\n"

ifeq ($(DJANGO_COMPATIBLE),1)
	@echo "Detected Django $(DJANGO_VERSION)"
else
	$(error Detected Django $(DJANGO_VERSION) < 1.9. The web monitor requires at least Django 1.9)
endif


install: webapp

webapp/core:
	# Make sure the install directories exist
	test -d $(prefix) || mkdir -m 0755 -p $(prefix)
	test -d $(prefix)/app || mkdir -m 0755 $(prefix)/app
	test -d $(prefix)/static || mkdir -m 0755 $(prefix)/static
	
	# Install application code
	cp $(app_dir)/manage.py $(prefix)/app
	cp -R $(app_dir)/live_data_server $(prefix)/app
	cp -R $(app_dir)/templates $(prefix)/app
	cp -R $(app_dir)/plots $(prefix)/app
	#cp -R reporting/static $(prefix)/app

	# The following should be done with the proper apache user
	#chgrp apache $(prefix)/static/web_monitor
	#chown apache $(prefix)/static/web_monitor

webapp: webapp/core
	# Collect the static files and install them
	cd $(prefix)/app; python manage.py collectstatic --noinput

	# Create migrations and apply them
	cd $(prefix)/app; python manage.py makemigrations
	cd $(prefix)/app; python manage.py migrate
	
	# Prepare web monitor cache: RUN THIS ONCE BY HAND
	#cd $(prefix)/app; python manage.py createcachetable webcache
	
	
	@echo "\n\nReady to go: run apachectl restart\n"
	
first_install: webapp/core
	# Modify and copy the wsgi configuration
	cp config/apache/apache_django_wsgi.conf /etc/httpd/conf.d

docker/pruneall: docker/compose/validate  ## stop all containers, then remove all containers, images, networks, and volumes
	$(DOCKER_COMPOSE) down --volumes
	docker system prune --all --volumes --force

docker/compose/validate:  ## validate the version of the docker-compose command. Exits quietly if valid.
	@./scripts/docker-compose_validate.sh $(DOCKER_COMPOSE)

local/docker/up: docker/compose/validate ## compose and start the service locally
	\cp ./config/docker-compose.envlocal.yml docker-compose.yml
	$(DOCKER_COMPOSE) up --build

.PHONY: check
.PHONY: first_install
.PHONY: help
.PHONY: install
.PHONY: webapp
.PHONY: webapp/core
.PHONY: docker/compose/validate
.PHONY: docker/pruneall
.PHONY: local/docker/up
