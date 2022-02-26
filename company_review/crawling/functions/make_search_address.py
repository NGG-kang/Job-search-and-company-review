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

jp = (
    JobPlanet.objects.all()
    .filter(search_address="")
    .only("address", "search_address", "company_pk")
)
kj = KreditJob.objects.all().filter(search_address="")
sm = Saramin.objects.all().filter(search_address="")


def jobplanet():
    print("시작")
    for i in jp:
        print(i.company_pk)
        address = i.data["주소"]
        if i.company_pk == "359268":
            continue
        address = address.replace("본사: ", "")
        _address = address.split(" ")
        if len(_address) >= 2:
            _address[0] = _address[0].replace("광역시", "")
            _address[0] = _address[0].replace(",", "")
            i.search_address = f"{_address[0]} {_address[1]}"
        else:
            i.search_address = address
        print(i.search_address)
        i.address = address
        i.save()


def kreditjob():
    print("시작")
    for i in kj:
        print(i.company_pk)
        _address = i.address.split(" ")
        if len(_address) >= 2:
            _address[0] = _address[0].replace("광역시", "")
            _address[0] = _address[0].replace(",", "")
            i.search_address = f"{_address[0]} {_address[1]}"
        else:
            i.search_address = i.address
            print(i.address)
        print(i.search_address)
        i.save()


def saramin():
    print("시작")
    for i in sm:
        print(i.company_pk)
        _address = i.address.split(" ")
        if len(_address) >= 2:
            _address[0] = _address[0].replace("광역시", "")
            _address[0] = _address[0].replace(",", "")
            i.search_address = f"{_address[0]} {_address[1]}"
        else:
            i.search_address = i.address
            print(i.address)
        print(i.search_address)
        i.save()


jobplanet()
kreditjob()
saramin()
