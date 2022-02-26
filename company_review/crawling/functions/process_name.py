import django
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.dirname(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


from crawling.models import JobPlanet, KreditJob, Saramin
import re
from datetime import timedelta
from django.utils import timezone

# jp = JobPlanet.objects.all().filter(name__regex=r"\([^)]*\)").only("name")
# kj = KreditJob.objects.all().filter(name__regex=r"\([^)]*\)").only("name")
# sm = Saramin.objects.all().filter(name__regex=r"\([^)]*\)").only("name")

one_week_ago = timezone.now().date() - timedelta(days=7)
jp = JobPlanet.objects.all().filter(created__gte=one_week_ago).only("name")
kj = KreditJob.objects.all().filter(created__gte=one_week_ago).only("name")
sm = Saramin.objects.all().filter(created__gte=one_week_ago).only("name")


def jobplanet():
    print("시작")
    for i in jp:
        _name = i.name
        i.name = re.sub(r"\([^)]*\)", "", i.name)
        i.name = re.sub(r"[^a-zA-Z0-9가-힣]", "", i.name)
        print(_name, i.name)
        i.save()


def kreditjob():
    print("시작")
    for i in kj:
        _name = i.name
        i.name = re.sub(r"\([^)]*\)", "", i.name)
        i.name = re.sub(r"[^a-zA-Z0-9가-힣]", "", i.name)
        print(_name, i.name)
        i.save()


def saramin():
    print("시작")
    for i in sm:
        _name = i.name
        i.name = re.sub(r"\([^)]*\)", "", i.name)
        i.name = re.sub(r"[^a-zA-Z0-9가-힣]", "", i.name)
        print(_name, i.name)
        i.save()


# jobplanet()
# kreditjob()
saramin()
