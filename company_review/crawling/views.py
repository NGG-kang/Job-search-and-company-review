from django.shortcuts import render
from .models import KreditJob, JobPlanet, Saramin, SearchResult
from crawling.search_jobs.search import search_and_save
import gc
from django.core import serializers

# Create your views here.


def search_result(request, **kwargs):

    if request.htmx:
        template = "result.html"
    else:
        template = "index.html"
    q = request.GET.get("q")
    if q:
        try:
            context = {"context": SearchResult.objects.filter(search_q=q).last().data}
            # raise SearchResult.DoesNotExist
        except SearchResult.DoesNotExist:
            all_jobs = search_and_save(q)
            context = {"context": all_jobs}
        gc.collect()
    else:
        context = {}
    return render(request=request, template_name=template, context=context)
