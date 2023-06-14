import uuid

import requests
import json

from rest_framework import status
from rest_framework.response import Response

from alert.models import Alert
from co2 import settings
from config.models import Config
from log.models import Log
from utils.SCB.get_access_token import get_access


def scb_inquiry_data(request, transaction_date, event_code, ref1, ref2, alert_id=None):
  if not Config.pull_value('scb_pg_enable'):
    return None

  scb_acc = get_access(request)
  if not scb_acc:
    raise Response(data='SCB Payment Gateway can\'t connect', status=status.HTTP_503_SERVICE_UNAVAILABLE)

  url = settings.SCB_INQUIRY_URL
  payload = ""
  headers = {
    'Content-Type': 'application/json',
    'resourceOwnerId': settings.SCB_APP_KEY,
    'authorization': 'Bearer %s' % str(scb_acc),
    'requestUId': str(uuid.uuid4()),
    'accept-language': 'EN',
  }
  ## Overwrite value for test
  # transaction_date = '2022-07-20'
  # event_code = '00300100'
  # ref1='JT220701PP003'
  # ref2='PP003H0000THB'

  url = url + '?billerId=%s&transactionDate=%s&eventCode=%s&reference1=%s&reference2=%s' % (
    settings.SCB_BILLER_ID,
    transaction_date,
    event_code,
    ref1,
    ref2
  )

  response = requests.request("GET", url, headers=headers, data=payload)

  try:
    data = json.loads(response.text)
  except Exception as error:
    Log.push(request, 'TRANSACTION', 'TOPUP', 1, 'Can\'t access to API',
             status.HTTP_401_UNAUTHORIZED, payload=payload, note=error)
    return
  if data and data['status']['code'] == 1000 and data['data']:
    if alert_id and Alert.objects.get(id=alert_id):
      alert = Alert.objects.get(id=alert_id)
      alert.status = 2
      alert.traceback = alert.traceback + '\n' + str(data) if alert.traceback else str(data)
      alert.save(update_fields=['status', 'traceback', 'datetime_update'])
    return data
  else:
    return
