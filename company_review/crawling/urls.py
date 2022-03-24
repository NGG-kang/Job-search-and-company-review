from django.urls import path
from crawling import views

urlpatterns = [
    path("", views.search_result, name="search"),
    path("update_company/", views.update_company, name="update_company"),
    path("add-search-info/", views.add_search_cron_beat, name="add-search-info"),
]
