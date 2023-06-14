from django.contrib import admin

from .models import Trigger, Template

@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'code',
        'datetime_update',
        'is_active'
    )
    search_fields = ['name', 'is_active']
    list_filter = ['is_active']
    readonly_fields = []


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'is_standard',
        'subject',
        'body',
        'event_trigger',
        'datetime_update',
    )
    list_select_related = ['event_trigger']
    list_filter = ['is_standard']
    search_fields = ['subject']
    readonly_fields = []

