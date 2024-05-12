#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

#until python manage.py migrate
#do
#    echo "Waiting for db to be ready..."
#    sleep 2
#done

python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"
