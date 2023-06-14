import json
import os
import sys

import django
from datetime import date, datetime

import requests
from django.conf import settings

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'co2.settings')
django.setup()

from account.models import Account

def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


if __name__ == '__main__':
    ma_acc_list = []
    done_list = []
    url = settings.CO2_CHAIN_API_URL + "/migration/wallet"
    for acc in Account.objects.filter(is_active=True):
        payload = json.dumps({
            "account_id": acc.id
        })

        headers = {
            'authorization': settings.CO2_CHAIN_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.__dict__)
        if response.status_code != 200 or response.status_code != 201:
            print('Have some thing wrong please try again')
            print('Done list : %s' % done_list)
        else:
            print('account id %s is fail to call API' % acc.id)
            ma_acc_list.append(acc.id)
            continue

        wallet_data = json.loads(response.text)
        if wallet_data.get('status', 'fail') == 'success' and wallet_data.get('bsc_public_key', None):
            acc.bsc_public_key = wallet_data.get('bsc_public_key')
            acc.save(update_fields=['bsc_public_key', 'datetime_update'])
            print('account id %s is success to migrate' % acc.id)
            done_list.append(acc.id)
        else:
            print('account id %s is fail to migrate' % acc.id)
            ma_acc_list.append(acc.id)
            continue
    print('This processing log \n success : %s \n fail : %s' % (done_list, ma_acc_list))



