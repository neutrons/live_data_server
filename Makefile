prefix := /var/www/livedata
app_dir := live_data_server

all:

	@echo "Run make install to install the workflow manager and the web app"
	
check:
	# Check dependencies
	@python -c "import django" || echo "\nERROR: Django is not installed: www.djangoproject.com\n"
	@python -c "import psycopg2" || echo "\nWARNING: psycopg2 is not installed: http://initd.org/psycopg\n"


install: webapp

	
webapp/core:
	# Make sure the install directories exist
	test -d $(prefix) || mkdir -m 0755 -p $(prefix)
	test -d $(prefix)/app || mkdir -m 0755 $(prefix)/app
	test -d $(prefix)/static || mkdir -m 0755 $(prefix)/static
	test -d $(prefix)/static/web_monitor || mkdir -m 0755 $(prefix)/static/web_monitor
	
	# The following should be done with the proper apache user
	#chgrp apache $(prefix)/static/web_monitor
	#chown apache $(prefix)/static/web_monitor
	
	# Install application code
	cp $(app_dir)/manage.py $(prefix)/app
	#cp -R reporting/static $(prefix)/app
	#cp -R reporting/templates $(prefix)/app
	cp -R $(app_dir)/$(app_dir) $(prefix)/app
	
	# Install apache config
	#cp -R reporting/apache $(prefix)

webapp: webapp/core
	# Collect the static files and install them
	cd $(prefix)/app; python manage.py collectstatic --noinput

	# Create the database tables. The database itself must have been
	# created on the server already


	# Create migrations and apply them
	cd $(prefix)/app; python manage.py makemigrations
	cd $(prefix)/app; python manage.py migrate
	
	# Prepare web monitor cache: RUN THIS ONCE BY HAND
	#cd $(prefix)/app; python manage.py createcachetable webcache
	
	
	@echo "\n\nReady to go: run apachectl restart\n"
	
first_install: webapp/core
	# Modify and copy the wsgi configuration
	cp apache/apache_django_wsgi.conf /etc/httpd/conf.d

    
.PHONY: check
.PHONY: install
.PHONY: webapp
.PHONY: webapp/core
.PHONY: first_install
