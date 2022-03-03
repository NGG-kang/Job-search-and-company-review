import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.dirname(BASE_DIR))
from crawling.search_jobs.saramin import get_saramin_search
from crawling.search_jobs.jobkorea import get_jobkorea_search
from celery import shared_task
from crawling.models import JobPlanet, KreditJob, Saramin, SearchResult
from itertools import chain
from django.core.cache import cache


def search_and_save_row(q, celery=False):
    print(q)
    saramin = get_saramin_search(q)
    jobkorea = get_jobkorea_search(q)
    all_jobs = list(chain(saramin, jobkorea))
    if celery:
        names = [i["name"] for i in list(chain(saramin, jobkorea))]
        s = Saramin.objects.filter(name__in=names)
        k = KreditJob.objects.filter(name__in=names)
        j = JobPlanet.objects.filter(name__in=names)

        def get_model_dict(s):
            if s:
                _s = dict()
                for i in s:
                    if i["name"] in _s:
                        _s[i["name"]].append(i)
                    else:
                        _s[i["name"]] = [i]
                return _s
            return None

        saramin_object = get_model_dict(
            s.values("name", "search_address", "company_pk", "data")
        )
        jobplanet_object = get_model_dict(
            j.values("name", "search_address", "company_pk", "data")
        )
        kreditjob_object = get_model_dict(
            k.values(
                "name",
                "search_address",
                "company_pk",
                "company_base_content",
                "company_info_data",
                "company_jobdam",
            )
        )

        def get_company_info_dict(i, value_dict):
            if i["name"] in value_dict:
                for j in value_dict[i["name"]]:
                    if i["work_place"] == j["search_address"]:
                        return j
                return None
            else:
                return None

        for i in all_jobs:
            company_info_list = list()
            company_info_list.append(get_company_info_dict(i, saramin_object))
            company_info_list.append(get_company_info_dict(i, jobplanet_object))
            company_info_list.append(get_company_info_dict(i, kreditjob_object))
            i["objs"] = company_info_list
        cache.set(q, all_jobs, 600)
        # SearchResult.objects.update_or_create(search_q=q, data=all_jobs)

    return all_jobs


@shared_task
def search_and_save(q, celery=False):
    search_and_save_row(q, celery)


if __name__ == "__main__":
    search_and_save_row("java", celery=True)
