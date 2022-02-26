#!/bin/bash

celery -A celeries.celery worker -B -E -l INFO &

python manage.py collectstatic 

exec "$@"
