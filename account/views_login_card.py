import json
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import login, authenticate
import requests
from django.conf import settings
from django.utils import timezone

from log.models import Log
from account.views_login_vekin import login_vekin
from account.caches import cached_account_profile
from .models import Account, Session
from .serializers import LoginCardSerializer
from card.models import Card
from config.models import Config


class LoginCardView(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    allow_redirects = True
    permission_classes = (AllowAny,)
    serializer_class = LoginCardSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            card = Card.objects.get(number=data.get('number', 0))
            if not card.account.check_password(data['password']):
                return Response(data={'detail': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)
        except Card.DoesNotExist:
            card = Card.create_card_account('The mall', data['type'], data['number'], data['password'])
            if not card:
                return Response(data={'detail': 'Can\'t create card account'}, status=status.HTTP_400_BAD_REQUEST)

            headers = {
                'authorization': settings.CO2_CHAIN_API_KEY,
                'Content-Type': 'application/json'
            }
            url = settings.CO2_CHAIN_API_URL + 'wallet/create_wallet'
            payload = json.dumps({
                'account_id': card.account.id,
                'mcard': True
            })

            response = requests.request(
                'POST',
                url,
                headers=headers,
                data=payload
            )

            if response.status_code != 200 or response.status_code != 201:
                Log.push(request, 'ACCOUNT', 'CREATE_WALLET', card.account, 'Have something wrong with API create wallet',
                         status.HTTP_200_OK, payload=response.__dict__)

            wallet_data = json.loads(response.text)
            if not wallet_data.get('public_key', None):
                Log.push(request, 'ACCOUNT', 'CREATE_WALLET', card.account, 'Have something wrong with API create wallet',
                         status.HTTP_200_OK, payload=response.__dict__)
            else:
                public_key = wallet_data.get('public_key', None)
                card.account.sol_public_key = public_key.get('sol', None)
                card.account.bsc_public_key = public_key.get('bsc', None)

            card.account.save()
        except Exception as e:
            print('card create()')
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        login(request, card.account, backend='django.contrib.auth.backends.ModelBackend')

        session_key = request.session.session_key
        request.session.set_test_cookie()
        if session_key is None:
            request.session.save()
            session_key = request.session.session_key
        Session.push(request.user, session_key)

        request.session.set_expiry(Config.pull_value('config-session-age'))

        result = cached_account_profile(card.account.id)
        result.update({
            'sessionid': request.session.session_key,
            'csrftoken': request.META['CSRF_COOKIE']
        })

        return Response(data=result, status=status.HTTP_202_ACCEPTED)
