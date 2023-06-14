import json

import requests
from celery import shared_task
from django.utils import timezone
from rest_framework import status

from account.models import Account
from activity.models import CarbonActivity
from alert.models import Alert
from co2 import settings
from log.models import Log
from transaction.models import Transaction
from utils.base_task import BaseAlertTask
from datetime import datetime


@shared_task(bind=True, base=BaseAlertTask, retry_kwargs={'max_retries': 3})
def task_sync_tree_data(self, alert_id, account_id):
    account = Account.objects.get(id=account_id)
    alert = Alert.objects.filter(id=alert_id).first()
    if not alert:
        return None
    alert.task_id = self.request.id
    alert.status = 2
    alert.save(update_fields=['task_id', 'status', 'datetime_update'])

    url = "https://ml-dev.vekin.co.th/tree-mng/v2/backend/get-tree-sync-data/%s" % account.email
    if not settings.CO2_CHAIN_API_KEY:
        Log.push(
            None,
            'ACTIVITY_TREE',
            'SYNC_DATA',
            account.id,
            'API KEY NOT SETTING',
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        alert.set_failed(
            traceback='Sync data Account %s unsuccessful, because key not set in environment' % account.id
        )
    payload = json.dumps({})
    headers = {
        'authorization': '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code != 200 and response.status_code != 201:
        # TODO : Transaction Token check here @jade
        Log.push(None, 'ACTIVITY_TREE',
                 'SYNC_DATA', account.id, 'Have something wrong with API sync data',
                 status.HTTP_200_OK, payload=response.__dict__)
        alert.set_failed(
            traceback='Sync data Account %s unsuccessful, because have something wrong with API sync data' % account.id
        )
        return None

    tree_data = json.loads(response.text)
    if not tree_data or not tree_data.get('data', None) or not tree_data.get('status', None) or \
            tree_data.get('status', None) != 'success':
        Log.push(None, 'ACTIVITY_TREE',
                 'SYNC_DATA', self.account, 'Have something wrong with API sync data',
                 status.HTTP_200_OK, payload=response.__dict__)
        alert.set_failed(
            traceback='Sync data Account %s unsuccessful, because have something wrong with API sync data' % account.id
        )
        return None

    tree_data_list = tree_data.get('data')
    for _tree in tree_data_list:
        dt_create = datetime.fromisoformat(_tree.get('create_date').replace('Z', '')) if _tree.get('create_date', None) else timezone.now()
        transaction = None
        transaction = Transaction.objects.create(
            account_id=account.id,
            transaction_hash='',
            source_key='',
            desc='Add new tree : %s - %s - %s' % (
                _tree.get('code_id', '-'),
                _tree.get('tree_category_name', '-'),
                _tree.get('tag_code', '-')),
            paid_by=account.get_full_name(),
            destination_key='',
            values=0.0,
            coin=-1,
            method=4,
            status=2,
            datetime_start=dt_create
        )

        CarbonActivity.objects.create(
            transaction_id=transaction.id,
            type=5,
            activity_code=_tree.get('code_id', '-'),
            activity_name=_tree.get('tree_category_name', '-'),
            activity_details=_tree.get('tag_code', '-'),
            coin=1,
            desc=json.dumps(_tree),
            values=0.0,
            carbon_saving=0.0
        )

    alert.status = 3
    alert.traceback = 'This account %s already deleted' % account_id
    alert.save(update_fields=['traceback', 'status', 'datetime_update'])
    return 'DONE'
