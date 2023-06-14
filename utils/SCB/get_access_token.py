import uuid

import requests
import json

from rest_framework import status

from co2 import settings
from config.models import Config
from log.models import Log


def get_access(request):
  if not Config.pull_value('scb_pg_enable'):
    return None
  url = settings.SCB_ACCESS_URL
  payload = json.dumps({
    "applicationKey": settings.SCB_APP_KEY,
    "applicationSecret": settings.SCB_SECRET_KEY
  })
  headers = {
    'Content-Type': 'application/json',
    'resourceOwnerId': settings.SCB_APP_KEY,
    'requestUId': str(uuid.uuid4()),
    'accept-language': 'EN',
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  try:
    data = json.loads(response.text)
  except Exception as error:
    Log.push(request, 'TRANSACTION', 'TOPUP', 1, 'Can\'t access to API',
             status.HTTP_401_UNAUTHORIZED, payload=payload, note=error)
    return
  if data and data['status']['code'] == 1000 and data['data'] and data['data']['accessToken']:
    return data['data']['accessToken']
  else:
    return
