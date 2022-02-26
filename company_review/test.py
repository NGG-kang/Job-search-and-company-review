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
from proxy import proxies


# sa = Saramin.objects.filter(name="쿠팡")
print(proxies)

# for s in sa:
#     j = JobPlanet.objects.filter(name=s.name, search_address=s.search_address)
#     k = KreditJob.objects.filter(name=s.name, search_address=s.search_address)
# # j = JobPlanet.objects.filter(name=s.name, search_address=s.search_address)
# # k = KreditJob.objects.filter(name=s.name, search_address=s.search_address)
# print(j, k)
