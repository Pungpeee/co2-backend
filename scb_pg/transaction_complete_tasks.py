import json
from datetime import datetime

import requests
from celery import shared_task
from django.conf import settings
from rest_framework import status

from alert.models import Alert
from log.models import Log
from notification_template.models import Trigger
from scb_pg.models import SCBPayment
from transaction.models import Transaction, Payment
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

@shared_task(bind=True)
def task_complete_transaction(self, scb_pg_id, status_details, alert_id):
    # Change it to filter VEK bill_payment_ref1='VEK' TODO: @Jade
    scb_pg = SCBPayment.objects.get(id=scb_pg_id)
    alert = Alert.objects.get(id=alert_id)
    alert.task_id = self.request.id
    alert.save(update_fields=['task_id', 'datetime_update'])

    payment = Payment.objects.filter(ref_code_1=scb_pg.bill_payment_ref1, ref_code_2=scb_pg.bill_payment_ref2).first()
    if not payment:
        alert.set_failed(traceback={'result': 'Raf 1,2 [%s, %s] have no in payment system' % (scb_pg.bill_payment_ref1, scb_pg.bill_payment_ref2)})
        Log.push(None, 'SCB_PAYMENT', 'CONFIRMATION_PAYMENT', None, 'Unknown Confirmation Payment', status.HTTP_404_NOT_FOUND)
        return

    payment.datetime_stamp = datetime.now()
    payment.save(update_fields=['datetime_stamp', 'datetime_update'])

    # TODO : @Jade check account is a same account with transaction account
    ## Check algo here
    transaction = Transaction.objects.select_related('account').get(id=payment.transaction_id)
    sim_name = float(settings.SIMILAR_NAME_ACCEPTION)
    if similar(transaction.account.get_full_name(), scb_pg.payer_name) < sim_name and similar(transaction.account.get_full_name_thai(), scb_pg.payer_name) < sim_name:
        alert.set_failed(
            traceback={'result': 'Raf 1,2 [%s, %s] this name payee not match' % (scb_pg.bill_payment_ref1, scb_pg.bill_payment_ref2)})
        Log.push(None, 'SCB_PAYMENT', 'CONFIRMATION_PAYMENT', None, 'Account name not match with payee name',
                 status.HTTP_406_NOT_ACCEPTABLE)
        transaction.status = -4
        transaction.datetime_end = datetime.now()
        transaction.save(update_fields=['status', 'datetime_end', 'datetime_update'])
        return

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
    if response.status_code != 200 or response.status_code != 201:
        Log.push(None, 'ACCOUNT', 'TOPUP_COIN', transaction.account, 'Have something wrong with API create wallet',
                 status.HTTP_406_NOT_ACCEPTABLE, payload=response.__dict__)
        alert.set_failed(traceback={'result': 'Something wrong with api'})
        return
    else:
        if _data and _data.get('transaction_hash', None):
            transaction.transaction_hash = _data.get('transaction_hash')
        if not transaction or transaction.method != 3:
            Log.push(None, 'TRANSACTION_NOTI',
                     'NOTIFICATION_WRONG', transaction.account, 'Have something wrong with this transaction',
                     status.HTTP_400_BAD_REQUEST, content_type=settings.CONTENT_TYPE('transaction.transaction'),
                     content_id=transaction.id
                     )
            return
        transaction.status = 2
        transaction.desc = status_details
        transaction.datetime_end = datetime.now()
        transaction.datetime_complete = datetime.now()
        transaction.save(update_fields=['status', 'datetime_end', 'desc', 'datetime_update', 'transaction_hash'])
        Log.push(None, 'ACCOUNT', 'TOPUP_COIN', transaction.account,
                 'Success topup coin', status.HTTP_200_OK, payload=response.__dict__)
        Transaction.send_topup_noti(transaction_id=transaction.id, topup_status=2)
        trigger = Trigger.get_code('top_up')
        trigger.send_notification(
            sender=None,
            inbox_type=1,
            inbox_content_type=settings.CONTENT_TYPE('transaction.transaction'),
            inbox_content_id=transaction.id,
            account_list=[transaction.account]
        )
    alert.status = 3
    alert.save(update_fields=['status', 'datetime_update'])
    return 'Done'
