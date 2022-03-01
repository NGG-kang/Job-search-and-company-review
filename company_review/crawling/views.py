from django.shortcuts import render
from .models import KreditJob, JobPlanet, Saramin, SearchResult
from crawling.search_jobs.search import search_and_save
import gc
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
        gc.collect()
    else:
        context = {}
    return render(request=request, template_name=template, context=context)
