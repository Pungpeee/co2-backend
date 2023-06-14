import json
import random
import string
import urllib

import jwt
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from analytic.models import Session2 as AnalyticSession
from config.models import Config
from log.models import Log
from term.models import Term
from utils.ip import get_client_ip
from .models import Account, Session
from .serializers import OauthValidateSerializer, AccountSerializer


def _push_log_oauth(request, message, status, payload={}, account=None, note=''):
    Log.push(
        request,
        'ACCOUNT',
        'ACCOUNT_LOGIN_OAUTH',
        account,
        message,
        status,
        payload=payload,
        note=note
    )


def validate_admd(request, data):
    _account = None
    payload = {}
    oauth_config = Config.pull_value('config-login-oauth-grant-code')
    if data['is_web']:
        client_id = oauth_config.get('client_id')
    else:
        client_id = oauth_config.get('client_id_mobile')
    oauth_config.update(
        {
            'client_id': urllib.parse.quote(client_id),
            'redirect_uri': '%s/account/validate/' % Config.pull_value('config-site-url'),
            'code': data['code']
        }
    )
    url_token = '{site}/{path_token}' \
                '?client_id={client_id}' \
                '&client_secret={client_secret}' \
                '&grant_type={grant_type}' \
                '&code={code}' \
                '&redirect_uri={redirect_uri}'.format(**oauth_config)

    response = requests.get(url_token)
    if response.status_code == 200:
        code_data = json.loads(response.text)
        id_token = code_data['id_token']
        payload['access_token'] = code_data['access_token']
    else:
        message = 'error_code_oauth'
        _push_log_oauth(request,
                        message,
                        response.status_code,
                        note=response.text, payload={'url': url_token, 'data': data})
        return _account, payload

    try:
        payload.update(jwt.decode(id_token, verify=False))
    except jwt.exceptions.DecodeError:
        message = 'error_decode_id_token'
        _push_log_oauth(request,
                        message,
                        status.HTTP_401_UNAUTHORIZED,
                        note=response.text, payload={'url': url_token, 'data': data})
        return _account, payload
    if 'info' in payload and 'aut' in payload:
        info = payload['info']
        aut = payload['aut']
    else:
        message = 'error_id_token'
        _push_log_oauth(request,
                        message,
                        status.HTTP_401_UNAUTHORIZED,
                        payload=payload)
        return _account, payload

    if aut['type'] == 'email_password':
        if 'username' in info and info['username']:
            username = info['username']
            email = info['username']
            firstname = info.get('firstname', username)
            lastname = info.get('lastname', '')
            facebook_id = ''
            _account = Account.objects.filter(email=email).order_by('-is_active').first()
            if not _account:
                _account = Account.objects.filter(username=email).order_by('-is_active').first()
        else:
            message = 'error_info'
            _push_log_oauth(request,
                            message,
                            status.HTTP_401_UNAUTHORIZED,
                            payload=payload)
            return _account, payload
    elif aut['type'] == 'facebook':
        if 'id' in info and info['id']:
            username = info['id']
            email = info.get('email', None)
            name = info.get('name', '').split(' ', 1)
            firstname = name[0]
            lastname = name[1] if len(name) >= 2 else ''
            facebook_id = info['id']
            if email:
                _account = Account.objects.filter(Q(facebook_user_id=facebook_id) | Q(email=email)).order_by(
                    '-is_active').first()
            else:
                _account = Account.objects.filter(facebook_user_id=facebook_id).order_by('-is_active').first()
        else:
            message = 'error_info'
            _push_log_oauth(request,
                            message,
                            status.HTTP_401_UNAUTHORIZED,
                            payload=payload)
            return _account, payload
    else:
        message = 'error_aut'
        _push_log_oauth(request,
                        message,
                        status.HTTP_401_UNAUTHORIZED,
                        payload=payload)
        return _account, payload

    if not _account:
        if not Account.is_unique_username(username):
            message = 'error_create_account_username_duplicate'
            _push_log_oauth(request,
                            message,
                            status.HTTP_409_CONFLICT,
                            payload=payload)
            return _account, payload
        _account = push_account(username, email, firstname, lastname, facebook_id)
        message = 'create_account'
        _push_log_oauth(request,
                        message,
                        status.HTTP_201_CREATED,
                        payload=payload,
                        account=_account)
    return _account, payload


def push_account(username, email, firstname, lastname, facebook_id=''):
    account = Account.objects.create(
        username=username,
        email=email,
        first_name=firstname,
        last_name=lastname,
        date_start=None,
        is_accepted_active_consent=not (Term.objects.filter(
            content_type_id=settings.CONTENT_TYPE('term.term').id,
            is_publish=True).exists())
    )
    if facebook_id:
        account.facebook_user_id = facebook_id
    password = ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation) for _ in
        range(12))
    account.set_password(password)
    account.save()
    return account


def logout_admd(request, account_id, session_key):
    oauth_config = Config.pull_value('config-login-oauth-grant-code')
    oauth_config.update(
        {
            'client_id': urllib.parse.quote(oauth_config.get('client_id')),
            'redirect_uri': '%s/account/validate/' % Config.pull_value('config-site-url'),
        }
    )
    user = request.user if request.user.is_authenticated else None
    for session in Session.objects.filter(account_id=account_id, session_key=session_key):
        if session.token:
            payload = {
                'client_id': oauth_config['client_id'],
                'state': oauth_config['state'],
                'access_token': session.token
            }
            url_logout = '{site}/{path_logout}'.format(**oauth_config)
            response = requests.post(url_logout, json=payload)
            if response.status_code == 200:
                message = 'logout_success'
                Log.push(request, 'ACCOUNT', 'ACCOUNT_LOGOUT_OAUTH', user,
                         message, status.HTTP_200_OK, payload=payload, note=response.text)
            else:
                message = 'logout_fail'
                Log.push(request, 'ACCOUNT', 'ACCOUNT_LOGOUT_OAUTH', user,
                         message, response.status_code, payload=payload, note=response.text)


class OauthValidateView(viewsets.GenericViewSet):
    queryset = Account.objects.none()
    serializer_class = OauthValidateSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if 'code' not in data:
            message = 'error_code_not_found'
            _push_log_oauth(request,
                            message,
                            status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'error_contact_admin'}, status=status.HTTP_400_BAD_REQUEST)

        _account = None
        payload = {}
        partner = int(Config.pull_value('config-login-oauth-grant-code-partner'))
        if partner == 1:
            _account, payload = validate_admd(request, data)

        if not _account:
            return Response({'detail': 'error_contact_admin'}, status=status.HTTP_400_BAD_REQUEST)

        account = authenticate(username=_account.username, password=None)
        if account is None:
            message = 'error_account_authenticate'
            _push_log_oauth(request,
                            message,
                            status.HTTP_401_UNAUTHORIZED,
                            payload=payload)
            return Response({'detail': 'error_contact_admin'}, status=status.HTTP_400_BAD_REQUEST)
        elif not account.is_active:
            message = 'error_account_inactive'
            _push_log_oauth(request,
                            message,
                            status.HTTP_406_NOT_ACCEPTABLE,
                            payload=payload)
            return Response({'detail': message}, status=status.HTTP_406_NOT_ACCEPTABLE)

        login(request, account)
        account.last_active = timezone.now()
        account.save()
        session_key = request.session.session_key
        if session_key is None:
            request.session.save()
            session_key = request.session.session_key
        Session.push(request.user, session_key, payload.get('access_token', None))
        if data['is_web']:
            source = 0
        else:
            source = 1
        ip = get_client_ip(request)
        AnalyticSession.push(account, session_key, source, ip)

        message = 'login_success'
        _push_log_oauth(request,
                        message,
                        status.HTTP_200_OK,
                        payload=payload)

        response = AccountSerializer(instance=account).data
        response['action'] = payload.get('aut', {}).get('action', None)
        return Response(data=response, status=status.HTTP_200_OK)
