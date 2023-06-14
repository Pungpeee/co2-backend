from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(blank=True, null=True)
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)

    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)
