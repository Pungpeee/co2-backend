import json
import logging

import requests
from celery import shared_task
from django.utils import timezone
from rest_framework import status

from account.models import Account
from activity.models import CarbonActivity
from alert.models import Alert
from django.conf import settings

from log.models import Log
from notification_template.models import Trigger
from utils.base_task import BaseAlertTask
from .models import Transaction


@shared_task(bind=True, base=BaseAlertTask)
def task_transaction_earn_coin(self, alert_id, transaction_id, carbon_activity_id):
    logger = logging.getLogger('transaction')
    alert = Alert.objects.filter(id=alert_id).first()
    alert.status = 2
    alert.save(update_fields=['status'])
    transaction = Transaction.pull(transaction_id)
    account = Account.objects.get(id=transaction.account_id)
    carbon_activity = CarbonActivity.objects.get(id=carbon_activity_id)
    coin_dict = dict(CarbonActivity.COIN_CHOICES)
    if transaction.status == -1:
        url = settings.CO2_CHAIN_API_URL + "transfer/send_token"

        payload = json.dumps({
            "to_address": transaction.account.sol_public_key,
            "account_id": transaction.account.id,
            "token_name": transaction.get_coin_display(),
            "amount": transaction.values
        })

        headers = {
            'authorization': settings.CO2_CHAIN_API_KEY,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        _data = json.loads(response.text)
        if response.status_code != 200 and response.status_code != 201:
            Log.push(None, 'TRANSACTION', 'EARN_COIN', transaction.account,
                     'Have something wrong with API wallet',
                     status.HTTP_406_NOT_ACCEPTABLE,
                     content_type=settings.CONTENT_TYPE('transaction.transaction'),
                     content_id=transaction.id,
                     payload=response.__dict__)
            transaction.status = -3
            transaction.save(update_fields=['status', 'datetime_update'])
            alert.status = -1
            alert.traceback = 'Have Something wrong with transaction'
            alert.save(update_fields=['json_kwargs', 'traceback', 'status', 'datetime_update'])
            return 'FAIL'
        else:
            if _data and _data.get('transaction_hash', None):
                transaction.transaction_hash = _data.get('transaction_hash')
            if not transaction or transaction.account.id is not account.id or transaction.method != 4:
                Log.push(None, 'TRANSACTION_NOTI',
                         'NOTIFICATION_WRONG', account, 'Have something wrong with this transaction',
                         status.HTTP_200_OK,
                         content_type=settings.CONTENT_TYPE('transaction.transaction'),
                         content_id=transaction_id,
                         payload=response.__dict__
                         )
                transaction.status = -3
                transaction.save(update_fields=['status', 'datetime_update'])
                alert.status = -1
                alert.traceback = 'Have Something wrong with transaction'
                alert.save(update_fields=['json_kwargs', 'traceback', 'status', 'datetime_update'])
                return 'FAIL'
            transaction.status = 2
            transaction.desc = 'Earn success'
            transaction.datetime_end = timezone.now()
            transaction.datetime_complete = timezone.now()
            transaction.save(update_fields=['status', 'datetime_end', 'desc', 'datetime_update', 'transaction_hash'])
            account = transaction.account
            account.carbon_saving = float(account.carbon_saving) + float(carbon_activity.carbon_saving) if isinstance(account.carbon_saving, float) and float(carbon_activity.carbon_saving) > 0.0 else account.carbon_saving
            account.save(update_fields=['carbon_saving', 'datetime_update'])
            Log.push(None, 'TRANSACTION', 'EARN_COIN', transaction.account,
                     'Success earn coin', status.HTTP_200_OK, payload=response.__dict__)

        trigger = Trigger.get_code('earn_coin')
        trigger.send_notification(
            sender=None,
            inbox_type=1,
            inbox_content_type=settings.CONTENT_TYPE('activity.carbonactivity'),
            inbox_content_id=carbon_activity_id,
            account_list=[account]
        )
        logger.info(
            '200 OK (%s) Earn %s %s Coin Success' %
            (
                account.username,
                carbon_activity.values,
                coin_dict[carbon_activity.coin]
            )
        )
        alert.status = 3
        alert.save(update_fields=['json_kwargs', 'status', 'datetime_update'])
        return 'Done'

    elif transaction.status != -1:
        alert.status = 3
        alert.traceback = 'Transaction already DONE, can not make it duplicate'
        alert.save(update_fields=['json_kwargs', 'traceback', 'status', 'datetime_update'])
        return 'Done'

    else:
        alert.status = -1
        alert.traceback = 'Have Something wrong with transaction'
        alert.save(update_fields=['json_kwargs', 'traceback', 'status', 'datetime_update'])
        return 'Fail'
