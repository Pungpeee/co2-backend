from django.contrib import admin
from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'account', 'type', 'provider']
    search_fields = ['id', 'number', 'account']
    list_filter = ['type', 'provider']
