import django
import os
import sys
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.dirname(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from crawling.models import JobPlanet, KreditJob, Saramin
from config.celery import get_saramin_company, jobplanet


company = Saramin.objects.all().only("name").distinct("name").order_by("name")
for i in company:
    print(i.name.strip())
    jobplanet.delay(i.name)


# company = KreditJob.objects.only("name").distinct("name").order_by("-name")[:100000]
# print(company)

# for i in company:
#     print(i.name.strip())
#     get_saramin_company.delay(i.name)
