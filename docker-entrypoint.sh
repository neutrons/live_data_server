#!/bin/sh
set -e

# wait for database
until PGPASSWORD=${DATABASE_PASS} psql -h "${DATABASE_HOST}" -U "${DATABASE_USER}" -d "${DATABASE_NAME}" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

cd /var/www/livedata/app

# collect static files
python manage.py collectstatic --noinput

# migrate django models
python manage.py flush --no-input
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# create superuser
python manage.py createsuperuser --username "${DATABASE_USER}" --email "${DATABASE_USER}@localhost" --noinput

# Create the webcache
python manage.py createcachetable webcache

# run application
gunicorn live_data_server.wsgi:application -w 2 -b :8000 --reload
