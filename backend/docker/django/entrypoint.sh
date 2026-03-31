#!/bin/sh
set -e
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
