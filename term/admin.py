from django.contrib import admin

from term.models import Term, Log


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'body',)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'term', 'datetime_create')
