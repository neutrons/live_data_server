#!/bin/sh
set -e

# Build the project
cd /usr/src; make install

# Create the webcache
cd /var/www/livedata/app; python manage.py createcachetable webcache

# Start the server
# apachectl restart
cd /var/www/livedata/app; python manage.py runserver 0.0.0.0:8000