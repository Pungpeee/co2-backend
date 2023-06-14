from django.contrib import admin

from .models import Mailer


@admin.register(Mailer)
class MailerAdmin(admin.ModelAdmin):
    list_display = ('id', 'to', 'subject', 'status', 'datetime_create')
    actions = ['send_mailer']
    search_fields = ['to', 'subject', 'status']
    readonly_fields = ['inbox', ]

    # ordering = ['to', 'status']

    @staticmethod
    def send_mailer(self, request, queryset):
        for sender in queryset:
            service = sender.settings['service']
            if service == 'DJANGO':
                sender.send_django()
            elif service == 'MAILGUN':
                sender.send_mailgun()
            else:
                pass
