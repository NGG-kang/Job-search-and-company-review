from django.test import TestCase

# Create your tests here.
from crawling.models import KreditJob, Saramin, JobPlanet
from django.core.cache import cache


def get_all_company_name():
    k = [i.name for i in KreditJob.objects.all().only("name").distinct("name")]
    s = [i.name for i in Saramin.objects.all().only("name").distinct("name")]
    j = [i.name for i in JobPlanet.objects.all().only("name").distinct("name")]
    k.extend(s)
    k.extend(j)
    k = set(k)
    k = list(k)
    cache.set("company_list", k, None)
