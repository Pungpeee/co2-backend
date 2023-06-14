import json

import requests
from django.conf import settings
from django.contrib.auth import login
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from analytic.models import Session2 as AnalyticSession
from config.models import Config
from log.models import Log
from term.models import Term, Consent
from utils.generator import generate_token
from utils.ip import get_client_ip
from .caches import cached_account_profile, cache_account_delete
from .models import Account, Session, KYCAccount, IdentityVerification
from .serializers import LoginSSOSerializer


def set_session(account, request, login_type, is_web):
    login(request, account, backend='django.contrib.auth.backends.ModelBackend')
    session_key = request.session.session_key
    if session_key is None:
        request.session.save()
        session_key = request.session.session_key
    Session.push(request.user, session_key)
    request.session.set_expiry(Config.pull_value('config-session-age'))

    if is_web:
        source = 0
    else:
        source = 1

    ip = get_client_ip(request)
    AnalyticSession.push(account, session_key, source, ip)
    Log.push(request, 'ACCOUNT_SSO', 'LOGIN_VEKIN', account, login_type + ' Login Success', status.HTTP_200_OK)


class LoginSSOView(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = LoginSSOSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        url = settings.SSO_URL + 'access_key/login/'

        try:
            session_id = request.session.session_key
            csrftoken = request.META['CSRF_COOKIE']
        except:
            session_id = None
            csrftoken = None

        payload = json.dumps({
            "username": data['username'],
            "password": data['password'],
            "site": data['site'] if 'site' in data and data['site'] else 'co2',
            "profile_url": data['profile_url'] if 'profile_url' in data and data['profile_url'] else settings.CO2_API_URL + '/backend/api/account/is-authenticated/',
            "sessionid": session_id if session_id else None,
            "csrftoken": csrftoken if csrftoken else None
        })
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            Log.push(request, 'ACCOUNT',
                     'CHECK_BALANCE', None, 'Have something wrong with SSO API',
                     status.HTTP_200_OK, payload=response.__dict__)
            return Response(data={'Have something wrong with SSO API'},
                            status=status.HTTP_400_BAD_REQUEST)
        sso_profile = json.loads(response.text)
        if not sso_profile or not sso_profile.get('external_id', None) or\
                not sso_profile.get('code', None) or \
                not sso_profile.get('username', None) or \
                sso_profile.get('is_active') == 'false':
            Log.push(request, 'ACCOUNT_SSO',
                     'SSO', None, 'Have no data from sso system',
                     status.HTTP_200_OK, payload=response.__dict__)
            return Response(data={'Have no data from sso system'}, status=status.HTTP_404_NOT_FOUND)
        cookie = response.cookies.get_dict()

        # check only username because co2 username == email
        account = Account.objects.filter(username=sso_profile.get('username', None)).first()
        username = sso_profile.get('username', None)
        email = sso_profile.get('email', None)
        external_id = sso_profile.get('external_id', None)
        code = sso_profile.get('code', None)
        full_name = sso_profile.get('full_name', '')
        first_name = full_name.split()[0] if full_name and full_name.split() else ''
        last_name = full_name.split()[1] if full_name and full_name.split() else ''

        # Check data
        if not username:
            return Response(data={'Username is require'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            email = username
        if not external_id or not code:
            return Response(data={'SSO not provide access key'}, status=status.HTTP_400_BAD_REQUEST)

        # Check account
        if account and not account.is_active:
            Log.push(request, 'ACCOUNT_SSO', 'SSO', account, 'This account is not active now',
                     status.HTTP_200_OK, payload=response.__dict__)
            return Response(data={'This account can\'t use while not active'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if not account:
            token = generate_token(32)
            _term = Term.objects.filter(
                content_type_id=settings.CONTENT_TYPE('term.term').id,
                is_publish=True).first()
            is_publish_term = bool(_term)
            _is_accept_active_consent = True if not is_publish_term else data.get('is_accepted_active_consent', False)

            account = Account.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_accepted_active_consent=not (Term.objects.filter(
                    content_type_id=settings.CONTENT_TYPE('term.term').id,
                    is_publish=True).exists()),
                extra=json.dumps({
                    'SSO': {
                        'external_id': external_id,
                        'code': code,
                        'session_id': cookie['sessionid'],
                        'csrf_token': cookie['csrftoken'],
                        'token': token
                    }
                }),
                is_verified_email=True,
                is_get_news=True,
                is_share_data=True,
                is_admin=False
            )
            KYCAccount.objects.create(
                account_id=account.id,
                title=account.title,
                first_name=account.first_name,
                first_name_thai=account.first_name_thai,
                middle_name=account.middle_name,
                middle_name_thai=account.middle_name_thai,
                last_name=account.last_name,
                last_name_thai=account.last_name_thai,
                id_card=account.id_card,
                laser_code=account.laser_code,
                id_front_image=account.id_front_image,
                id_back_image=account.id_back_image,
                id_selfie_image=account.id_selfie_image,
                is_accepted_kyc_consent=account.is_accepted_kyc_consent,
                kyc_status=account.kyc_status,
                phone=account.phone,
                date_birth=account.date_birth
            )
            payload = json.dumps({
                "account_id": account.id
            })

            if not settings.CO2_CHAIN_API_KEY:
                Log.push(
                    request,
                    'ACCOUNT_WALLET',
                    'VEKIN',
                    account,
                    'API KEY FOR CREATE WALLET NOT SETTING',
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            headers = {
                'authorization': settings.CO2_CHAIN_API_KEY,
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code != 200 or response.status_code != 201:
                Log.push(request, 'ACCOUNT', 'CREATE_WALLET', account, 'Have something wrong with API create wallet',
                         status.HTTP_200_OK, payload=response.__dict__)

            wallet_data = json.loads(response.text)
            if not wallet_data.get('public_key', None):
                Log.push(request, 'ACCOUNT', 'CREATE_WALLET', account, 'Have something wrong with API create wallet',
                         status.HTTP_200_OK, payload=response.__dict__)
            else:
                public_key = wallet_data.get('public_key', None)
                account.sol_public_key = public_key.get('sol', None)
                account.bsc_public_key = public_key.get('bsc', None)

            if _is_accept_active_consent and is_publish_term:
                Consent.objects.create(account=account, term=_term)

            account.set_password(token)
            account.last_active = timezone.now()
            account.save()

            site_url = Config.pull_value('config-site-url-app-link')
            Account.create_verify_email(
                email=account.email,
                token=account.code,
                site_url=site_url
            )

            if Config.pull_value('config-verify-email-is-enabled'):
                IdentityVerification.send_verification(account, 1, 1)  # Send verify email
        else:
            account.first_name = first_name
            account.last_name = last_name
            account.is_accepted_active_consent = not (Term.objects.filter(
                content_type_id=settings.CONTENT_TYPE('term.term').id,
                is_publish=True).exists())
            account.extra = json.dumps({
                'SSO': {
                    'external_id': external_id,
                    'code': code,
                    'session_id': cookie['sessionid'],
                    'csrf_token': cookie['csrftoken']
                }
            })
            account.is_verified_email = True
            account.is_get_news = True
            account.is_share_data = True
        account.save()
        cache_account_delete(account.id)
        set_session(account, request, 'SSO', False)
        result = cached_account_profile(account.id)
        if json.loads(account.extra) and json.loads(account.extra)['SSO']:
            result.update(json.loads(account.extra))
        return Response(data=result, status=status.HTTP_200_OK)
