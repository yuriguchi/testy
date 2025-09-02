#!/bin/sh
echo "Waiting for postgres..."
while ! nc -z $POSTGRES_SERVICE_HOST $POSTGRES_SERVICE_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"
python manage.py migrate --no-input
python manage.py seed_db
python manage.py collectstatic --no-input
gunicorn root.asgi:application -c scripts/gunicorn.conf.py
