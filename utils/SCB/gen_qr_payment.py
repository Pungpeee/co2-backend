import base64
import os
import string
import uuid
import random

from PIL import Image

import requests
import json
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.response import Response

from co2 import settings
from config.models import Config
from log.models import Log
from transaction.models import Transaction, Payment
from .get_access_token import get_access
from ..QR import make_qr
from ..datetime import convert_to_local


def ref_code_generator(transaction_id):
  transaction = Transaction.pull(transaction_id)
  if transaction and transaction.status == 1:
    ref1 = transaction.get_coin_display() + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20 - len(transaction.get_coin_display())))
    ref2 = 'TP%s' % transaction.id
    ref2 = ref2 + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20 - len(ref2)))
    return ref1, ref2 if not Payment.objects.filter(ref_code_1=ref1, ref_code_2=ref2).first() else ref_code_generator(transaction_id)
  else:
    return '', ''

def gen_qr_payment(request, transaction_id, payment_id, thb_value):
  transaction = Transaction.pull(transaction_id)
  if not Config.pull_value('scb_pg_enable'):
    transaction.set_cancel()
    return

  scb_acc = get_access(request)
  if not scb_acc:
    Log.push(request, 'TRANSACTION', 'TOPUP', -1, 'SCB Payment Gateway can\'t connect',
             status.HTTP_503_SERVICE_UNAVAILABLE)
    transaction.set_cancel()
    raise Response(data='SCB Payment Gateway can\'t connect', status=status.HTTP_503_SERVICE_UNAVAILABLE)

  ref_1, ref_2 = ref_code_generator(transaction_id)
  if not ref_1 or not ref_2:
    transaction.set_cancel()
    return

  payment = Payment.objects.get(id=payment_id)
  if not payment:
    Log.push(request, 'TRANSACTION', 'TOPUP', -1, 'Payment not found',
             status.HTTP_404_NOT_FOUND)
    transaction.set_cancel()
    return

  url = settings.SCB_GEN_QR_PAYMENT
  payload = json.dumps({
    "qrType": "PP",
    "ppType": "BILLERID",
    "expiryDate": convert_to_local(transaction.datetime_create + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
    "numberOfTimes": 1,
    "ppId": settings.SCB_BILLER_ID,
    "amount": float(thb_value),
    "ref1": ref_1,
    "ref2": ref_2,
    "ref3": settings.SCB_BILLER_REF
  })
  request_uid = str(uuid.uuid1())

  headers = {
    "Content-Type": "application/json",
    "authorization": "Bearer %s" % str(scb_acc),
    "resourceOwnerId": settings.SCB_APP_KEY,
    "requestUId": request_uid,
    "accept-language": "EN",
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  try:
    data = json.loads(response.text)
  except Exception as error:
    Log.push(request, 'TRANSACTION', 'TOPUP', -1, 'Can\'t generate QRCODE',
             status.HTTP_400_BAD_REQUEST, payload=payload, note=error)
    transaction.set_cancel()
    return
  if data and data['status']['code'] == 1000 and data['data'] and data['data']['qrImage'] and data['data']['qrRawData']:
    # qrcode = make_qr.to_image(data['data']['qrRawData'])
    # Convert base 64 to img way
    encoded_data = data['data']['qrImage']
    decoded_data = base64.b64decode((encoded_data))

    now = datetime.now()
    p = 'transaction/qrcode/%s-%02d' % (now.year, now.month)
    path = os.path.join(settings.MEDIA_ROOT, *p.split('/'))
    f = '%s_%s.png' % (payment.transaction_id, request_uid)
    filename = '%s/%s' % (path, f)
    if not os.path.isdir(path):
      os.makedirs(path)

    img_file = open(filename, 'wb')
    img_file.write(decoded_data)
    img_file.close()

    # img = qrcode.resize((512, 512), Image.NEAREST)
    # img.save(filename)

    payment.qrcode = '%s/%s' % (p, f)
    payment.code = request_uid
    payment.ref_code_1 = ref_1
    payment.ref_code_2 = ref_2
    payment.save(update_fields=['qrcode', 'code', 'ref_code_1', 'ref_code_2', 'datetime_update'])
    return payment
  else:
    Log.push(request, 'TRANSACTION', 'TOPUP', -1, 'Can\'t generate QRCODE',
             status.HTTP_400_BAD_REQUEST, payload=payload)
    transaction.set_cancel()
    return
