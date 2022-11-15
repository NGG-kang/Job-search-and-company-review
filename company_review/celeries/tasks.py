from celery import shared_task
import traceback
from celeries.get_compnay_info import (
    get_kreditjob_company,
    get_saramin_company,
    get_jobplanet_company,
)
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone


@shared_task
def get_saramin_info(name, update=False):
    get_saramin_company(name, update)


@shared_task
def get_jobplanet_info(name, update=False):
    get_jobplanet_company(name, update)


@shared_task
def get_kreditjob_info(name, update=False):
    try:
        get_kreditjob_company(name, update)
    except:
        print(traceback.print_exc())

@shared_task
def change_task_interval():
    tasks = PeriodicTask.objects.exclude(name="celery.backend_cleanup")
    interval = IntervalSchedule.objects.get_or_create(every=6, period='hours')[0]
    tasks.interval = interval
    tasks.save()