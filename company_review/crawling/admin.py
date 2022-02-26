from django.contrib import admin
from crawling.models import JobPlanet, KreditJob, Saramin, SearchResult
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html


# Register your models here.
@admin.register(JobPlanet)
class JobPlanetAdmin(admin.ModelAdmin):
    list_display = ("name", "company_pk", "address", "search_address", "created")
    search_fields = ["search_address", "company_pk", "name"]

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
    list_display = (
        "id",
        "name",
        "address",
        "search_address",
        "company_pk",
        "jobdam",
        "created",
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
    )
    search_fields = ["search_address", "company_pk", "name"]


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ("search_q", "data", "created", "updated")
    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {"widget": JSONEditorWidget},
    }
