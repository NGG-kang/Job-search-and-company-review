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
    saramin, saramin_length = get_saramin_search(q)
    jobkorea, jobkorea_length = get_jobkorea_search(q)
    all_jobs = list(chain(saramin, jobkorea))
    if celery:
        names = [i["name"] for i in list(chain(saramin, jobkorea))]
        s = Saramin.objects.filter(name__in=names).only("name", "search_address", "company_pk", "data")
        k = KreditJob.objects.filter(name__in=names).only(
                "name",
                "search_address",
                "company_pk",
                "company_base_content",
                # "company_info_data",
                "company_jobdam",
            )
        j = JobPlanet.objects.filter(name__in=names).only("name", "search_address", "company_pk", "data")

        def get_model_dict(objs):
            if objs:
                obj = dict()
                for i in objs:
                    if i["name"] in obj:
                        obj[i["name"]].append(i)
                    else:
                        obj[i["name"]] = [i]
                return obj
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
                # "company_info_data",
                "company_jobdam",
            )
        )

        def get_company_info_dict(job, value_dict):
            if value_dict and job["name"] in value_dict:
                for j in value_dict[job["name"]]:
                    if job["work_place"] == j["search_address"]:
                        return j
                return [val for val in value_dict[job["name"]]]
            else:
                return None

        saramin_list = list()
        jobkorea_list = list()
        for index, job in enumerate(all_jobs):
            company_info_list = list()
            company_info_list.append(get_company_info_dict(job, saramin_object))
            company_info_list.append(get_company_info_dict(job, jobplanet_object))
            company_info_list.append(get_company_info_dict(job, kreditjob_object))
            job["objs"] = company_info_list
            if index < saramin_length:
                saramin_list.append(job)
                continue
            if index < saramin_length + jobkorea_length:
                jobkorea_list.append(job)
                continue
        all_jobs = {'saramin': saramin_list, 'jobkorea': jobkorea_list}
        cache.set(q, all_jobs, None)
    return all_jobs


@shared_task
def search_and_save(q, celery=False):
    search_and_save_row(q, celery)


if __name__ == "__main__":
    search_and_save_row("java", celery=True)
