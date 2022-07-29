from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from .models import KreditJob, JobPlanet, Saramin
from celeries.celery import get_company_info
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.core.cache import cache
from django.contrib import messages
import traceback


def search_result(request, **kwargs):
    context = {}    
    if request.htmx:
        template = "result.html"
    else:
        template = "index.html"

    q = request.GET.get("q")
    if q:
        data = cache.get(q)
        if data:
            context = {"context": data}
    try:
        PeriodicTask.objects.get(name=q)
        data = True
    except PeriodicTask.DoesNotExist:
        data = False
    context["data"] = data
    context["tasks"] = PeriodicTask.objects.all().values("name", "task", "last_run_at", "interval__period", "interval__every", )
    return render(request=request, template_name=template, context=context)


def update_company(request, **kwargs):
    if request.htmx:
        if request.POST:
            company = request.POST.get("company")
            get_company_info.apply_async(kwargs={'name': company, 'update': True})
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
                if not company:
                    return HttpResponseBadRequest("Need company data")
                interval = IntervalSchedule.objects.get_or_create(every=1, period='minutes')[0]
                PeriodicTask.objects.create(
                    name=company,
                    task="crawling.search_jobs.search.search_and_save",
                    enabled=True,
                    interval=interval,
                    args=f'["{company}", "True"]',
                    priority=0,
                    queue='search'
                )
                messages.add_message(request, messages.INFO, 'Hello world.')
                return render(request=request, template_name="result.html")
            except Exception as e:
                print(traceback.print_exc())
                print(e)
                return HttpResponseBadRequest("Already save company")
    return HttpResponseBadRequest("using method post")