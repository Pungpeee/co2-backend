import json

from django.db import models
from account.models import Account
from utils.generator import generate_token
import requests
from django.conf import settings


class Card(models.Model):
    TYPE_CHOICES = [
        ('m_card', 'M Card'),
    ]

    provider = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    number = models.CharField(max_length=16, unique=True, db_index=True)
    holder = models.CharField(max_length=255, blank=True, null=True, default='')
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)

    datetime_create = models.DateTimeField(auto_now_add=True)
    datetime_update = models.DateTimeField(auto_now=True)

    @staticmethod
    def create_card_account(provider, card_type, number, password, holder=''):
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'x-ibm-client-id': settings.THEMALL_X_IBM_CLIENT_ID,
            'X-ibm-client-secret': settings.THEMALL_X_IBM_CLIENT_SECRET
        }
        payload = json.dumps({
            "mobile_number": password
        })
        response = requests.request(
            'POST',
            f'{settings.THEMALL_PARTNER_URL}{number}/validatemobile',
            headers=headers,
            data=payload
        )

        if response.status_code != 200:
            return None

        while True:
            token = generate_token(32)
            if not Account.objects.filter(code=token).exists():
                break

        account = Account.objects.create(
            code=token,
            username=None,
            email=None,
            title=0,
            gender=0,
            first_name='',
            middle_name='',
            last_name='',
            date_birth=None,
            address='',
            phone='',
            extra='{}',
            is_accepted_active_consent=True,
            is_get_news=False,
            is_share_data=False,
            id_card='',
            sol_public_key=None,
            bsc_public_key=None
        )
        account.set_password(password)
        account.save()

        card = Card.objects.create(
            provider=provider,
            type=card_type,
            number=number,
            holder=holder if holder != '' else account.first_name + ' ' + account.last_name,
            account=account
        )

        return card
