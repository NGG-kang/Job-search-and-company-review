from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from .models import KreditJob, JobPlanet, Saramin, SearchResult
from celeries.celery import get_company_info
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
