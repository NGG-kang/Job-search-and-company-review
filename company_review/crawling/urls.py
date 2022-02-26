from django.urls import path
from .views import search_result

urlpatterns = [
    path("", search_result, name="search"),    
]
