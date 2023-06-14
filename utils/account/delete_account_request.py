import uuid

import requests
import json

from rest_framework import status

from account.models import Account
from co2 import settings
from config.models import Config
from log.models import Log


def delete_account_bc(account_id):
  if not Config.pull_value('block-chain-enable'):
    return None

  url = settings.CO2_CHAIN_API_URL+'/transfer/delete_account'
  payload = json.dumps({
    "account_id": account_id
  })
  headers = {
    'authorization': settings.CO2_CHAIN_API_KEY,
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  try:
    data = json.loads(response.text)
  except Exception as error:
    Log.push(None, 'ACCOUNT', 'WALLET', Account.objects.get(id=1), 'Can\'t access to API',
             status.HTTP_400_BAD_REQUEST, payload=payload, note=error)
    return
  return data if data else None
