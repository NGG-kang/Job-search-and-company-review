#!/bin/bash

./wait_for_it.sh db:5432

celery -A celeries.celery worker -B -l INFO -Q search,saramin,kreditjob,jobplanet --concurrency=6 --scheduler django_celery_beat.schedulers:DatabaseScheduler