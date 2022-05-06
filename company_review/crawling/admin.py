from django.contrib import admin
from crawling.models import JobPlanet, KreditJob, Saramin, SearchResult
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html


from django.core.paginator import Paginator
from django.core.cache import cache

# Modified version of a GIST I found in a SO thread
class CachingPaginator(Paginator):
    def _get_count(self):

        if not hasattr(self, "_count"):
            self._count = None

        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)

            except:
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


# Register your models here.
@admin.register(JobPlanet)
class JobPlanetAdmin(admin.ModelAdmin):
    list_display = ("name", "company_pk", "address", "search_address", "created", "updated")
    search_fields = ["search_address", "company_pk", "name"]
    show_full_result_count = False
    paginator = CachingPaginator

    def address(self, obj):
        return obj.data["주소"]


class OnlyJobdamFilter(admin.SimpleListFilter):
    title = _("jobdam")
    parameter_name = "company_jobdam"

    def lookups(self, request, model_admin):
        return (("all", _("모든 잡담")), ("jobdam", _("1개 이상")))

    def queryset(self, request, queryset):
        if self.value() == "all":
            return queryset
        elif self.value() == "jobdam":
            return queryset.filter(company_jobdam__count__gt=0)


@admin.register(KreditJob)
class KreditJobAdmin(admin.ModelAdmin):
    list_filter = (OnlyJobdamFilter,)
    search_fields = ["search_address", "company_pk", "name"]
    show_full_result_count = False
    paginator = CachingPaginator
    list_display = (
        "id",
        "name",
        "address",
        "search_address",
        "company_pk",
        "jobdam",
        "created",
        "updated"
    )

    def jobdam(self, obj):
        if obj.company_jobdam["count"] > 0:
            return {
                i["TITLE"]: format_html(
                    f"https://www.kreditjob.com/board/{i['JOBDOM_NO']}"
                )
                for i in obj.company_jobdam["board"]
            }
        return {}

    search_fields = ["name"]
    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Saramin)
class SaraminAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "search_address",
        "company_pk",
        "created",
        "updated"
    )
    show_full_result_count = False
    paginator = CachingPaginator
    search_fields = ["search_address", "company_pk", "name"]


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ("search_q", "data", "created", "updated")
    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {"widget": JSONEditorWidget},
    }
