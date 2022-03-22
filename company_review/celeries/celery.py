from celery import Celery
import django
import os
import sys
from pathlib import Path

app = Celery(
    "config",
    broker="redis://default@redis//",
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(os.path.dirname(BASE_DIR))
django.setup()

from crawling.search_jobs.search import search_and_save
from celeries.get_compnay_info import (
    get_kreditjob_company,
    get_saramin_company,
    get_jobplanet_company,
)
from crawling.models import KreditJob, Saramin, JobPlanet
from django.core.cache import cache
import time


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwrags):
    sender.add_periodic_task(
        300.0, search_and_save.s(kwrags["q"], kwrags["celery"]), name="django search"
    )


@app.task(bind=True)
def get_company_info(self, name, update=False):
    get_jobplanet_company(name, update)
    get_saramin_company(name, update)
    get_kreditjob_company(name, update)


@app.task(bind=True)
def get_company_info_update(self):
    company_list = cache.get("company_list")
    if not company_list:
        k = [i.name for i in KreditJob.objects.all().only("name").distinct("name")]
        s = [i.name for i in Saramin.objects.all().only("name").distinct("name")]
        j = [i.name for i in JobPlanet.objects.all().only("name").distinct("name")]
        k.extend(s)
        k.extend(j)
        k = set(k)
        k = list(k)
        cache.set("company_list", k, None)
    for name in company_list:
        print(name)
        get_company_info.delay(name, True)
