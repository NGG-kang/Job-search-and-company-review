from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from .models import KreditJob, JobPlanet, Saramin
from celeries.celery import get_company_info
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.core.cache import cache
from django.contrib import messages
import traceback
import requests
import json

with open('./crawling/search_jobs/wanted_category.json', 'r') as f:
    wanted_category = json.load(f)

def init_context(request):
    context = dict()
    q = request.GET.get("q", "")
    data = cache.get(q)
    if q:
        if data:
            context = {"context": data}
        try:
            PeriodicTask.objects.get(name=q)
            data = True
        except PeriodicTask.DoesNotExist:
            wanted_res = requests.get(f"https://www.wanted.co.kr/api/v4/tags/autocomplete?kinds=SKILL&keyword={q}")
            data = False
            if wanted_res.json()['results']:
                context['wanted_q'] = wanted_res.json()['results']
            context['wanted_category'] = wanted_category
    context["q"] = q     
    context["data"] = data
    context["tasks"] = PeriodicTask.objects.all().values("name", "task", "last_run_at", "interval__period", "interval__every", )
        
    return context

def search_result(request, **kwargs):
    context = {}    
    if request.htmx:
        template = "result.html"
    else:
        template = "index.html"
    
    context = init_context(request)
    return render(request=request, template_name=template, context=context)


def update_company(request, **kwargs):
    if request.htmx:
        if request.POST:
            company = request.POST.get("company")
            get_company_info.apply_async(kwargs={'name': company, 'update': True})
            return JsonResponse({"message": "success"})
    return HttpResponseBadRequest("using method post")


def add_search_cron_beat(request):
    context = init_context(request)
    if request.htmx:
        if request.POST:
            try:
                search_q = request.POST.get("search_q", "")
                wanted_q = request.POST.get("wanted_q", "")
                wanted_category = request.POST.get("wanted_category", "")
                wanted = {"wanted_category": "", "wanted_q": ""}
                if not search_q:
                    return HttpResponseBadRequest("Need company data")
                if wanted_q:
                    wanted = {"wanted_category": wanted_category, "wanted_q": wanted_q}
                    
                interval = IntervalSchedule.objects.get_or_create(every=30, period='minutes')[0]
                PeriodicTask.objects.create(
                    name=search_q,
                    task="crawling.search_jobs.search.search_and_save",
                    enabled=True,
                    interval=interval,
                    kwargs=json.dumps({"q": search_q, "wanted": wanted}),
                    priority=0,
                    queue='search'
                )
                messages.add_message(request, messages.SUCCESS, 'Save Success')
                return render(request=request, template_name="result.html", context=context)
            except Exception as e:
                print(traceback.print_exc())
                print(e)
                return HttpResponseBadRequest("Already save company")
    return HttpResponseBadRequest("using method post")