#!/bin/sh
set -e

# start cron, export root env variables
service cron start
env >>/etc/environment

# wait for database
until PGPASSWORD=${DATABASE_PASS} psql -h "${DATABASE_HOST}" -U "${DATABASE_USER}" -d "${DATABASE_NAME}" -c '\q'; do
  echo >&2 "Postgres is unavailable - sleeping"
  sleep 1
done

cd /var/www/livedata/app

# collect static files
python manage.py collectstatic --noinput

# migrate django models
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# create superuser
#echo "from django.contrib.auth.models import User; User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_USERNAME}@example.com', '${DJANGO_SUPERUSER_PASSWORD}')" | python manage.py shell

# Create the webcache
python manage.py createcachetable webcache
python manage.py ensure_adminuser --username=${DJANGO_SUPERUSER_USERNAME} --email='workflow@example.com' --password=${DJANGO_SUPERUSER_PASSWORD}

# run application
${COVERAGE_RUN} gunicorn config.wsgi:application -w 2 -b :8000 --reload
