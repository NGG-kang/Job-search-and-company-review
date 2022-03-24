from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from .models import KreditJob, JobPlanet, Saramin
from celeries.celery import get_company_info
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.core.cache import cache

# Create your views here.


def search_result(request, **kwargs):

    if request.htmx:
        template = "result.html"
    else:
        template = "index.html"
    q = request.GET.get("q")
    if q:
        data = cache.get(q)
        if data:
            context = {"context": data}
        else:
            # search_and_save.delay(q, True)
            context = {"data": "None"}
    else:
        context = {}
    return render(request=request, template_name=template, context=context)


def update_company(request, **kwargs):
    if request.htmx:
        if request.POST:
            company = request.POST.get("company")
            get_company_info.delay(company, True)
            return JsonResponse({"message": "success"})
    return HttpResponseBadRequest("using method post")


def search_company(request, **kwargs):
    template = "search_company.html"
    company = request.GET.get("company")
    if company:
        s = Saramin.objects.filter(name=company).values()
        j = JobPlanet.objects.filter(name=company).values()
        k = KreditJob.objects.filter(name=company).values()
        context = {"saramin": s, "jobplanet": j, "kreditjob": k}
    return render(request=request, template_name=template, context=context)


def add_search_cron_beat(request):
    if request.htmx:
        if request.POST:
            try:
                company = request.POST.get("company")
                interval = IntervalSchedule.objects.get(id=1)
                PeriodicTask.objects.create(
                    name=company,
                    task="crawling.search_jobs.search.search_and_save",
                    enabled=True,
                    interval=interval
                )
                return JsonResponse({"message": "success"})
            except Exception:
                return HttpResponseBadRequest("Already save company")            
    return HttpResponseBadRequest("using method post")
