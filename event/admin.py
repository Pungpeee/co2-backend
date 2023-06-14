from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_active', 'start_datetime', 'end_datetime']
