from django.contrib import admin

from account.models import Account
from .models import Inbox, Member, Count, Read


@admin.register(Inbox)
class Inbox(admin.ModelAdmin):
    list_display = ('id', 'account', 'content_type', 'datetime_send', 'datetime_create')
    actions = ['notification_fcm', 'notification_email', 'notification']
    search_fields = ['account__email']
    readonly_fields = ['account', 'content_type']

    def notification_fcm(self, request, queryset):
        for inbox in queryset:
            inbox.send_notification_fcm()

    def notification_email(self, request, queryset):
        for inbox in queryset:
            inbox.send_notification_email()

    def notification(self, request, queryset):
        for inbox in queryset:
            inbox.send_notification()


admin.site.register(Read)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'inbox', 'datetime_create')
    search_fields = ('account__first_name', 'account__last_name', 'account__code', 'account__sol_public_key',
                     'account__bsc_public_key', 'account__email', 'account__username')
    ordering = ('-inbox__datetime_create',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'account':
            kwargs["queryset"] = Account.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Count)
class CountAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'count')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'account':
            kwargs["queryset"] = Account.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def reset_zero(self, request, queryset):
        for count in queryset:
            count.count = 0
            count.save()
