#!/bin/sh

# Wait for the database to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
  echo "Waiting for DB..."
done
echo "PostgreSQL is ready."

#until python manage.py migrate
#do
#    echo "Waiting for db to be ready..."
#    sleep 2
#done

python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"
