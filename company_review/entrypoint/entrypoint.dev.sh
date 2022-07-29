#!/bin/bash

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

celery -A celeries.celery worker -B -l INFO -Q search,saramin,kreditjob,jobplanet --scheduler django_celery_beat.schedulers:DatabaseScheduler &

exec "$@"
