from __future__ import print_function

from urllib.request import urlopen

import facebook
from django.contrib.auth import login
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models import Q
from google.auth.transport import requests as request_google
from google.oauth2 import id_token
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from analytic.models import Session2 as AnalyticSession
from config.models import Config
from log.models import Log
from utils.ip import get_client_ip
from .models import Account, Session
from .serializers import LoginSocialSerializer, AccountSerializer
from term.models import Term

import jwt
import requests
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

GRAPH_API_VERSION = 3.1


def login_facebook(request, token):
    if not Config.pull_value('config-is-enable-facebook-authentication'):
        return {'error_message': 'facebook authentication not enable'}, status.HTTP_406_NOT_ACCEPTABLE

    try:
        graph = facebook.GraphAPI(access_token=token, version=GRAPH_API_VERSION)
        args = {'fields': 'id,name,first_name,last_name,email,gender'}
        data = graph.get_object('me', **args)
        profile_url = 'http://graph.facebook.com/{0}/picture?type=large'.format(data['id'])
        print('data here : ', data)
        if 'error' not in data:
            if 'email' in data:
                account = Account.objects.filter(Q(facebook_user_id=data['id']) | Q(email=data['email'])).first()
                email = data['email']
            else:
                account = Account.objects.filter(facebook_user_id=data['id']).first()
                email = None

            if not account:
                gender, _gender = 0, data.get('gender', '')
                if not bool(_gender):
                    if _gender == 'male':
                        gender = 1
                    elif _gender == 'female':
                        gender = 2
                account = Account.objects.create(
                    username=data['id'],
                    email=email,
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    facebook_user_id=data['id'],
                    is_accepted_active_consent=not (Term.objects.filter(
                        content_type_id=settings.CONTENT_TYPE('term.term').id,
                        is_publish=True).exists())
                )

            if not account.facebook_user_id:
                account.facebook_user_id = data['id']

            check_new_image(account, profile_url)
            account.last_active = timezone.now()
            account.save(update_fields=['facebook_user_id'])
            set_session(account, request, 'facebook', False)
            return data, status.HTTP_200_OK
        else:
            # error from facebook
            return data, status.HTTP_401_UNAUTHORIZED
    except ValueError as e:
        return {'error_message': 'Exception : %s' % e}, status.HTTP_401_UNAUTHORIZED


    # except facebook.GraphAPIError:
    #     return {'error_message': 'invalid token'}, status.HTTP_401_UNAUTHORIZED


# TOOL
# https://developers.google.com/oauthplayground/
#
# SAMPLE RESPONSE
# {'aud': '919849732892-uad9bk52k6o3j99a6sbjmi09ld7n50kn.apps.googleusercontent.com',
#  'azp': '919849732892-emk10g86q8qr6kesagb6nr7mgn1jkcsd.apps.googleusercontent.com',
#  'email': 'ult3mate@gmail.com',
#  'email_verified': True,
#  'exp': 1556619469,
#  'family_name': 'Adhipanyasarij',
#  'given_name': 'Pattadon',
#  'iat': 1556615869,
#  'iss': 'https://accounts.google.com',
#  'locale': 'en',
#  'name': 'Pattadon Adhipanyasarij',
#  'picture': 'https://lh3.googleusercontent.com/-KZYMycakTiQ/AAAAAAAAAAI/AAAAAAAAB8A/JAl0zeos3lQ/s96-c/photo.jpg',
#  'sub': '101982582567108191128'}


def login_google(request, token):
    if not Config.pull_value('config-is-enable-google-authentication'):
        return {'error_message': 'google authentication not enable'}, status.HTTP_406_NOT_ACCEPTABLE

    try:
        data = id_token.verify_oauth2_token(token, request_google.Request(),
                                            Config.pull_value('config-google-app-id'))

        if data['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return {'error_message': 'Your email address not from google account'}, status.HTTP_401_UNAUTHORIZED

        google_unique_id = data['sub']
        account = Account.objects.filter(Q(google_user_id=google_unique_id) | Q(email=data.get('email', ''))).first()

        if not account:
            gender, _gender = 0, data.get('gender', '')
            if not bool(_gender):
                if _gender.lower() == 'male':
                    gender = 1
                elif _gender.lower() == 'female':
                    gender = 2

            account = Account.objects.create(
                username=google_unique_id,
                email=data.get('email', ''),
                first_name=data.get('given_name', ''),
                last_name=data.get('family_name', ''),
                google_user_id=google_unique_id,
                is_accepted_active_consent=not (Term.objects.filter(
                    content_type_id=settings.CONTENT_TYPE('term.term').id,
                    is_publish=True).exists())
            )
            if data.get('picture', None):
                check_new_image(account, data['picture'])

        if not account.google_user_id:
            account.google_user_id = google_unique_id

        if 'picture' in data and data['picture'] is not None:
            check_new_image(account, data['picture'])
        account.last_active = timezone.now()
        account.save(update_fields=['last_active', 'google_user_id'])
        set_session(account, request, 'google', False)
        return data, status.HTTP_200_OK
    except ValueError as e:
        Log.push(None, 'Google Login Error', 'Error',
                 None,
                 status='Google Login Error',
                 payload='Error Google Exception : %s' % Config.pull_value('config-google-app-id'),
                 status_code=400)
        # return {'error_message': 'invalid token id ' + token}, status.HTTP_401_UNAUTHORIZED
        return {'error_message': 'Exception : %s' % e}, status.HTTP_401_UNAUTHORIZED


def set_session(account, request, social_type, is_web):
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
    Log.push(request, 'SOCIAL_LOGIN', 'VEKIN', account, 'Social Login Success' + social_type, status.HTTP_200_OK)


def check_new_image(account, image_url):
    if not account.image:
        save_image(account, image_url)

    # Check update
    # else:
    #     old_data_img_base_64 = base64.b64encode(account.image.read())
    #     new_data_img_base_64 = base64.b64encode(requestUrl.get(image_url).content)
    #     if old_data_img_base_64 != new_data_img_base_64:
    #         save_image(account, image_url)


def save_image(account, image_url):
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(urlopen(image_url).read())
    img_temp.flush()
    account.image.save(f'image_{account.id}.png', File(img_temp))


class AppleOAuth2:

    def do_auth(self, request, access_token, *args, **kwargs):

        if not Config.pull_value('config-is-enable-apple-id-authentication'):
            return {'error_message': 'apple authentication not enable'}, status.HTTP_406_NOT_ACCEPTABLE

        _time = timezone.now()

        response_data = {}
        client_id, client_secret = self.get_key_and_secret(_time)
        headers = {'content-type': "application/x-www-form-urlencoded"}
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': access_token,
            'grant_type': 'authorization_code',
        }

        res = requests.post('https://appleid.apple.com/auth/token', data=data, headers=headers)
        response_dict = res.json()
        id_token = response_dict.get('id_token', None)

        if id_token:
            decoded = jwt.decode(id_token, '', verify=False)
            response_data.update({'email': decoded['email']}) if 'email' in decoded else None
            response_data.update({'uid': decoded['sub']}) if 'sub' in decoded else None
            response_data.update({'aud': decoded['aud']}) if 'aud' in decoded else None
            response_data.update({'iss': decoded['iss']}) if 'iss' in decoded else None
            response_data.update({'iat': decoded['iat']}) if 'iat' in decoded else None
            response_data.update({'exp': decoded['exp']}) if 'exp' in decoded else None
        else:
            Log.push(request, 'ACCOUNT_LOGIN', 'APPLE_LOGIN', None, 'Invalid Token', status.HTTP_401_UNAUTHORIZED,
                     payload=response_dict)
            return {'error_message': 'invalid token'}, status.HTTP_401_UNAUTHORIZED

        apple_unique_id = response_data['uid']

        # if response_data['aud'] != Config.pull_value('config-apple-auth-client-id'):
        #     Log.push(request, 'ACCOUNT_LOGIN', 'APPLE_LOGIN', None, 'Invalid aud', status.HTTP_401_UNAUTHORIZED,
        #              payload=response_dict)
        #     return {'error_message': 'invalid token'}, status.HTTP_401_UNAUTHORIZED
        if response_data['iss'] != 'https://appleid.apple.com':
            Log.push(request, 'ACCOUNT_LOGIN', 'APPLE_LOGIN', None, 'Invalid iss', status.HTTP_401_UNAUTHORIZED,
                     payload=response_dict)
            return {'error_message': 'invalid token'}, status.HTTP_401_UNAUTHORIZED
        if int(response_data['iat']) > int(response_data['exp']):
            Log.push(request, 'ACCOUNT_LOGIN', 'APPLE_LOGIN', None, 'Invalid time', status.HTTP_401_UNAUTHORIZED,
                     payload=response_dict)
            return {'error_message': 'invalid token'}, status.HTTP_401_UNAUTHORIZED

        account = Account.objects.filter(
            Q(apple_user_id=apple_unique_id) | Q(email=response_data.get('email', ''))).first()

        if not account:
            gender, _gender = 0, data.get('gender', '')
            if not bool(_gender):
                if _gender.lower() == 'male':
                    gender = 1
                elif _gender.lower() == 'female':
                    gender = 2

            account = Account.objects.create(
                username=apple_unique_id,
                email=response_data.get('email', ''),
                first_name=response_data.get('email', ''),
                last_name='',
                apple_user_id=apple_unique_id,
                is_accepted_active_consent=not (Term.objects.filter(
                    content_type_id=settings.CONTENT_TYPE('term.term').id,
                    is_publish=True).exists())
            )

        if not account.apple_user_id:
            account.apple_user_id = apple_unique_id

        account.last_active = timezone.now()
        account.save(update_fields=['last_active', 'apple_user_id'])
        set_session(account, request, 'apple', False)

        return response_data, status.HTTP_200_OK

    def get_key_and_secret(self, _time):
        headers = {
            'kid': Config.pull_value('config-apple-auth-key-id')
        }

        payload = {
            'iss': Config.pull_value('config-apple-auth-team-id'),
            'iat': _time,
            'exp': _time + timedelta(days=180),
            'aud': 'https://appleid.apple.com',
            'sub': Config.pull_value('config-apple-auth-client-id')
        }
        client_secret = jwt.encode(
            payload,
            Config.pull('config-apple-auth-private-key').value_text,
            algorithm='ES256',
            headers=headers
        ).decode("utf-8")
        return Config.pull_value('config-apple-auth-client-id'), client_secret


class LoginSocialView(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = LoginSocialSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data['social_type'] == 'facebook':
            response_data, status_response = login_facebook(request, data['token'])
            account = Account.objects.filter(
                Q(facebook_user_id=response_data.get('id')) | Q(email=response_data.get('email'))).first()
        elif data['social_type'] == 'google':
            response_data, status_response = login_google(request, data['token'])
            account = Account.objects.filter(
                Q(google_user_id=response_data.get('sub')) | Q(email=response_data.get('email'))).first()
        elif data['social_type'] == 'apple':
            instance = AppleOAuth2()
            response_data, status_response = instance.do_auth(request, data['token'])
            account = Account.objects.filter(
                Q(apple_user_id=response_data.get('uid')) | Q(email=response_data.get('email'))).first()
        else:
            response_data, status_response = {'error_message': 'social_type invalid'}, status.HTTP_400_BAD_REQUEST
            account = None

        return Response(data=AccountSerializer(account).data, status=status_response)
