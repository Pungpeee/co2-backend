import os
import sys

import django
from datetime import date, datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'co2.settings')
django.setup()

from account.models import Account
from account_log.models import AccountLog

def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


if __name__ == '__main__':
    for account in Account.objects.all():
        acc_log = AccountLog.objects.filter(account_id=account.id).first()
        if acc_log:
            status = -99
            if account.is_active and (account.first_name or account.last_name or account.first_name_thai or account.last_name_thai):
                status = 1
            elif not account.is_active and (account.first_name or account.last_name or account.first_name_thai or account.last_name_thai):
                status = -2
            elif account.is_active and not (account.first_name or account.last_name or account.first_name_thai or account.last_name_thai):
                status = -1
            elif not account.is_active and not (account.first_name or account.last_name or account.first_name_thai or account.last_name_thai):
                status = 2
            acc_log.gender = account.gender if account and account.gender and isinstance(int(account.gender), int) else 0
            acc_log.age = int(calculate_age(account.date_birth)) if account and account.date_birth else -1
            acc_log.status = status
            acc_log.save()
        else:
            AccountLog.objects.create(
                account_id=account.id,
                gender = account.gender,
                age = calculate_age(account.date_birth) if account.date_birth else -1,
                status = account.status
            )
