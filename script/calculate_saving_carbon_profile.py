import os
import sys

import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'co2.settings')
django.setup()

from account.models import Account
from django.db.models import Sum

from activity.models import CarbonActivity
from transaction.models import Transaction

if __name__ == '__main__':
    for account in Account.objects.all():
        transaction_id_list = list(Transaction.objects.filter(account_id=account.id, method=4).values_list('id', flat=True))
        print(' account id %s \n account email : %s \n transaction_id_list : %s' % (account.id, account.email, transaction_id_list))
        carbon_activity = CarbonActivity.objects.filter(transaction_id__in=transaction_id_list).aggregate(Sum('carbon_saving'))
        if carbon_activity and carbon_activity['carbon_saving__sum']:
            print(account.id, account.get_full_name(), carbon_activity)
            account.carbon_saving = int(carbon_activity['carbon_saving__sum'])
            account.save(update_fields=['carbon_saving', 'datetime_update'])
        else:
            print(account.id, account.get_full_name(), carbon_activity)
            account.carbon_saving = 0.0
            account.save(update_fields=['carbon_saving', 'datetime_update'])