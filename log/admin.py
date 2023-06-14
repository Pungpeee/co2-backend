from django.contrib import admin

from .models import Log, RequestLog


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'group',
        'code',
        'account_username',
        'account_email',
        'status',
        'status_code',
        'ip',
        'datetime_create'
    )
    search_fields = ['account_username', 'account_email', 'payload']

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'account',
        'method',
        'path',
        'status_code',
        'timestamp'
    )
    search_fields = ['account_username', 'method', 'payload', 'path']

