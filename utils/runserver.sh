#!/bin/bash

sh /utils/init-crypto.sh;

if [ "$DEBUG" = "0" ]; then
  echo "Running in production mode...";
  sh /utils/migrate.sh;
  sh /utils/collectstatic.sh;
  gunicorn docker_django.wsgi:application -w $GUNICORN_WORKERS --bind :8081 --reload;
else
  echo "Running in development mode...";
  python /app/manage.py runserver 0.0.0.0:8081;
fi