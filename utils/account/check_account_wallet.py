import uuid

import requests
import json

from rest_framework import status

from account.models import Account
from co2 import settings
from config.models import Config
from log.models import Log


def get_access(account_id):
  if not Config.pull_value('block-chain-enable'):
    return None

  url = settings.CO2_CHAIN_API_URL+'/wallet/get_account/%s' % account_id
  payload = {}
  headers = {
    'authorization': settings.CO2_CHAIN_API_KEY
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  try:
    data = json.loads(response.text)
    if response.status_code != 200 and response.status_code != 201:
      Log.push(None, 'ACCOUNT',
               'CHECK_BALANCE', Account.objects.filter(id=account_id).first(),
               'Have something wrong with API check balance wallet',
               status.HTTP_200_OK, payload=response.__dict__)
      return None
  except Exception as error:
    Log.push(None, 'ACCOUNT', 'WALLET', Account.objects.get(id=1), 'Can\'t access to API',
             status.HTTP_400_BAD_REQUEST, payload=payload, note=error)
    return
  return data if data else None
