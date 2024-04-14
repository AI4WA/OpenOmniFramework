#!/bin/bash

# Wait for Postgres to become available.
until PGPASSWORD=$DB_PASS psql -h "$DB_SERVICE" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
python manage.py migrate

echo "Starting emotion detection worker"
python manage.py emoji
