from datetime import date

from django.contrib import admin

from account.models import Account
from .models import AccountLog


def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


@admin.register(AccountLog)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'account_id',
        'gender',
        'age',
        'status'
    )
    actions = ['update']

    @staticmethod
    def update(self, request, queryset):
        for acc_log in queryset:
            account = Account.objects.get(acc_log.account_id)
            if acc_log:
                status = acc_log.status
                if account.is_active and (
                        account.first_name or account.last_name or account.first_name_thai or account.last_name_thai):
                    status = 1
                elif not account.is_active and (
                        account.first_name or account.last_name or account.first_name_thai or account.last_name_thai):
                    status = -2
                elif account.is_active and not (
                        account.first_name or account.last_name or account.first_name_thai or account.last_name_thai):
                    status = -1
                elif not account.is_active and not (
                        account.first_name or account.last_name or account.first_name_thai or account.last_name_thai):
                    status = 2

                acc_log.account_id = account.id,
                acc_log.gender = account.gender,
                acc_log.age = calculate_age(account.date_birth) if account.date_birth else -1,
                acc_log.status = status
                acc_log.save()
