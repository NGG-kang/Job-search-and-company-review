#!/bin/bash

celery -A celeries.celery worker -B -l INFO -Q search,saramin,kreditjob,jobplanet --concurrency=3 --scheduler django_celery_beat.schedulers:DatabaseScheduler &

python manage.py collectstatic --noinput

exec "$@"
