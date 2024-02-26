#!/bin/bash
# Docker entrypoint script.

# Wait for Postgres to become available.
until PGPASSWORD=$DB_PASS psql -h "$DB_SERVICE" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
python manage.py migrate

# run command to create superuser, also make sure if the user already exists then skip
echo "from django.contrib.auth import get_user_model; User = get_user_model(); username = 'admin'; email = 'admin@local.test'; password = 'password'; admin_exists = User.objects.filter(username=username).exists(); not admin_exists and User.objects.create_superuser(username, email, password) or None;" | python manage.py shell


python manage.py runserver 0.0.0.0:8000