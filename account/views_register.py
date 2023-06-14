import json

import requests
from django.conf import settings
from django.contrib.auth import login
from django.core.validators import validate_email, ValidationError
from django.utils import timezone
from rest_framework import mixins
from rest_framework import status, viewsets
from rest_framework.exceptions import NotAcceptable
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from account.models import IdentityVerification, KYCAccount
from analytic.models import Session2 as AnalyticSession
from config.models import Config
from log.models import Log
from notification_template.models import Trigger
from term.models import Term, Consent
from utils.generator import generate_token
from utils.ip import get_client_ip
from .models import Account, Session
from .serializers import RegisterSerializer, AccountSerializer


def send_email_verification(account_id):
    account = Account.objects.filter(id=account_id).first()
    if not account:
        return Response(data={'Have no account or email for verification'}, status=status.HTTP_404_NOT_FOUND)
    title = 'Please verify your email address.'
    trigger = Trigger.get_code('new_account')


def register(request, data, is_web):
    url = settings.CO2_CHAIN_API_URL + "wallet/create_wallet"
    config_register_value = Config.pull_value('config-register-form-co2')
    all_field = config_register_value['field_list']

    database_standard_field = {
        'username', 'email', 'password', 'confirm_password', 'title', 'first_name',
        'last_name', 'gender', 'date_birth', 'address', 'phone', 'is_accepted_active_consent',
        'code', 'sol_public_key', 'bsc_public_key', 'middle_name', 'id_card',
    }
    param_extra_field = {}
    # Check Empty Field
    for field in all_field:
        if not field['is_optional']:
            if field['key'] not in data:
                return {'detail': '%s_is_required' % field['key']}, status.HTTP_428_PRECONDITION_REQUIRED

        value = data.get(field['key'], None)

        if field['key'] in data and value and field['key'] not in str(database_standard_field):
            param_extra_field[field['key']] = value

        min_length = field.get('min_length', None)
        max_length = field.get('max_length', None)
        if min_length and value and len(value) < int(min_length) and max_length is None:
            return {'detail': '%s_length_error' % field['key']}, status.HTTP_400_BAD_REQUEST
        if max_length and value and len(value) > int(max_length) and min_length is None:
            return {'detail': '%s_length_error' % field['key']}, status.HTTP_400_BAD_REQUEST
        if max_length and value and len(value) > int(max_length) or min_length and value and len(value) < int(
                min_length):
            return {'detail': '%s_length_error' % field['key']}, status.HTTP_400_BAD_REQUEST
    username = None
    if data.get('email'):
        email = Account.objects.filter(email__iexact=data.get('email', '').strip()).first()
        username = data.get('email', '')
        if email:
            return {'detail': 'email_has_been_already_use'}, status.HTTP_409_CONFLICT
        try:
            validate_email(data.get('email'))
        except ValidationError:
            return {'detail': 'error_email_format'}, status.HTTP_400_BAD_REQUEST

    if data['password'] != data['confirm_password']:
        return {'detail': 'password_not_match'}, status.HTTP_400_BAD_REQUEST

    if not data.get('is_accepted_active_consent', False) and Term.objects.filter(
            content_type_id=settings.CONTENT_TYPE('term.term').id,
            is_publish=True).exists():
        return {'detail': 'please_accept_terms_condition'}, status.HTTP_400_BAD_REQUEST

    _term = Term.objects.filter(
        content_type_id=settings.CONTENT_TYPE('term.term').id,
        is_publish=True).first()
    is_publish_term = bool(_term)
    _is_accept_active_consent = True if not is_publish_term else data.get('is_accepted_active_consent', False)

    try:
        param_extra_field = json.dumps(param_extra_field)
    except:
        pass

    id_card = data.get('id_card', '')
    if id_card:
        id_card = Account.id_card_encrypt(id_card)

    # TODO : Create and Update public key

    public_key = None

    while True:
        token = generate_token(32)
        if not Account.objects.filter(code=token).exists():
            break

    _account = Account.objects.create(
        code=token,
        username=username.strip().lower(),
        email=data.get('email', '').strip().lower() if data.get('email') else None,
        title=data.get('title', 0),
        gender=data.get('gender', 0),
        first_name=data.get('first_name', ''),
        middle_name=data.get('middle_name', ''),
        last_name=data.get('last_name', ''),
        date_birth=data.get('date_birth') if data.get('date_birth') else None,
        address=data.get('address', ''),
        phone=data.get('phone', ''),
        extra=param_extra_field,
        is_accepted_active_consent=_is_accept_active_consent,
        is_get_news=data.get('is_get_news', False),
        is_share_data=data.get('is_share_data', False),
        id_card=id_card,
        sol_public_key=public_key,
        bsc_public_key=public_key
    )

    KYCAccount.objects.create(
        account_id=_account.id,
        title=_account.title,
        first_name=_account.first_name,
        first_name_thai=_account.first_name_thai,
        middle_name=_account.middle_name,
        middle_name_thai=_account.middle_name_thai,
        last_name=_account.last_name,
        last_name_thai=_account.last_name_thai,
        id_card=_account.id_card,
        laser_code=_account.laser_code,
        id_front_image=_account.id_front_image,
        id_back_image=_account.id_back_image,
        id_selfie_image=_account.id_selfie_image,
        is_accepted_kyc_consent=_account.is_accepted_kyc_consent,
        kyc_status=_account.kyc_status,
        phone=_account.phone,
        date_birth=_account.date_birth
    )

    payload = json.dumps({
        "account_id": _account.id
    })

    if not settings.CO2_CHAIN_API_KEY:
        Log.push(
            request,
            'ACCOUNT_WALLET',
            'VEKIN',
            _account,
            'API KEY FOR CREATE WALLET NOT SETTING',
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    headers = {
        'authorization': settings.CO2_CHAIN_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200 or response.status_code != 201:
        Log.push(request, 'ACCOUNT', 'CREATE_WALLET', _account, 'Have something wrong with API create wallet',
                 status.HTTP_200_OK, payload=response.__dict__)

    wallet_data = json.loads(response.text)
    if not wallet_data.get('public_key', None):
        Log.push(request, 'ACCOUNT', 'CREATE_WALLET', _account, 'Have something wrong with API create wallet',
                 status.HTTP_200_OK, payload=response.__dict__)
    else:
        public_key = wallet_data.get('public_key', None)
        _account.sol_public_key = public_key.get('sol', None)
        _account.bsc_public_key = public_key.get('bsc', None)

    if _is_accept_active_consent and is_publish_term:
        Consent.objects.create(account=_account, term=_term)

    _account.set_password(data['password'])
    _account.last_active = timezone.now()
    _account.save()

    site_url = Config.pull_value('config-site-url-app-link')
    Account.create_verify_email(
        email=_account.email,
        token=_account.code,
        site_url=site_url
    )

    if Config.pull_value('config-verify-email-is-enabled'):
        IdentityVerification.send_verification(_account, 1, 1)  # Send verify email

    login(request, _account, backend='django.contrib.auth.backends.ModelBackend')

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
    AnalyticSession.push(_account, session_key, source, ip)
    # TODO add register mail reaction
    # Inbox.
    Log.push(request, 'ACCOUNT_REGISTER', 'VEKIN', _account, 'Register Successful', status.HTTP_201_CREATED)
    return AccountSerializer(_account).data, status.HTTP_201_CREATED


class RegisterView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.all()
    allow_redirects = True
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        if not Config.pull_value('config-is-enable-register'):
            raise NotAcceptable
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response_data, status_response = register(request, request.data, False)
        return Response(data=response_data, status=status_response)

    def list(self, request, *args, **kwargs):
        if not Config.pull_value('config-is-enable-register'):
            raise NotAcceptable
        config_register_form = Config.pull_value('config-register-form-co2')
        return Response(config_register_form)
