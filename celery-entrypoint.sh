#!/bin/sh

# Wait for the database to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
  echo "Waiting for DB..."
done
echo "PostgreSQL is ready."

exec "$@"
