import json

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from rest_framework import status

from alert.models import Alert
from log.models import Log
from transaction.models import Transaction
from utils.base_task import BaseAlertTask


@shared_task(bind=True, base=BaseAlertTask)
def task_transaction_swap_token(self, transaction_id, alert_id):
    transaction = Transaction.objects.get(id=transaction_id)
    alert = Alert.objects.get(id=alert_id)
    alert.task_id = self.request.id
    alert.save(update_fields=['task_id', 'datetime_update'])

    url = settings.CO2_CHAIN_API_URL + "swap/swap_token"

    payload = json.dumps({
        "account_id": transaction.account.id,
        "sol_amount": transaction.values
    })

    headers = {
        'authorization': settings.CO2_CHAIN_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    _data = json.loads(response.text)
    if response.status_code != 200 and response.status_code != 201:
        Log.push(None, 'TRANSACTION', 'SWAP', transaction.account, 'Have something wrong with API create wallet',
                 status.HTTP_406_NOT_ACCEPTABLE, payload=response.__dict__)
        alert.set_failed(traceback={'result': 'Something wrong with api'})
        transaction.status = -2
        transaction.datetime_end = timezone.now()
        transaction.save(update_fields=['status', 'datetime_end', 'datetime_update'])
        return
    else:
        transaction.status = 2
        transaction.datetime_end = timezone.now()
        transaction.datetime_complete = timezone.now()
        transaction.save(update_fields=['status', 'datetime_end', 'datetime_update', 'datetime_complete'])
        Log.push(None, 'TRANSACTION', 'SWAP', transaction.account,
                 'Success Swap Coin', status.HTTP_200_OK, payload=response.__dict__)
    alert.status = 3
    alert.save(update_fields=['status', 'datetime_update'])
    return 'Done'
