from email.policy import default
from django.db import models


class Timestamp(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class JobsAbsctractModel(Timestamp):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=300, default="")
    company_pk = models.CharField(max_length=100, unique=True)
    data = models.JSONField(blank=True, default=dict)
    search_address = models.CharField(max_length=100, default="", blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class JobPlanet(JobsAbsctractModel):
    pass


class KreditJob(JobsAbsctractModel):
    company_base_content = models.JSONField(blank=True)
    company_info_data = models.JSONField(blank=True)
    company_jobdam = models.JSONField(blank=True)


class Saramin(JobsAbsctractModel):
    pass


class JobKorea(JobsAbsctractModel):
    pass


class SearchResult(Timestamp):
    search_q = models.CharField(max_length=50, blank=True)
    data = models.JSONField(blank=True)
