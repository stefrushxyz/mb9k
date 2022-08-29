#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$RESET_DB" = "1" ]
then
    echo "Preparing database..."

    python manage.py sqlflush | python manage.py dbshell
    python manage.py migrate
    python manage.py loaddata fixtures.json

    echo "Database ready"
fi

exec "$@"

