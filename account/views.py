from datetime import timedelta

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import requests
import json

from account.models import Account, RequestDelete, UtilityToken
from alert.models import Alert
from config.models import Config
from log.models import Log
from mailer.tasks import send_mail
from .account_delete_tasks import task_delete_account
from .serializers import DeleteAccountSerializer, AccountSerializer
from utils.generator import generate_token


class AccountDeleteView(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.none()
    serializer_class = DeleteAccountSerializer
    
    @action(methods=['DELETE'], detail=False, url_path='confirm/(?P<token>\w+)')
    def delete(self, request, *args, **kwargs):
        token = self.kwargs.get('token')
        if not token:
            # for check data (token) in API reqeuest from front
            Log.push(
                request, 'ACCOUNT', 'CONFIRM_DELETE', request.user,
                'Have no token in request', status.HTTP_400_BAD_REQUEST
            )
            return Response(data={'result': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        account = Account.objects.get(id=request.user.id)
        del_req = RequestDelete.objects.filter(account=account, token=token).last()

        if not del_req:
            return Response(data={'result': 'Have no request before'}, status=status.HTTP_404_NOT_FOUND)
        elif del_req.datetime_create + timedelta(days=1) >= timezone.now():
            Log.push(request, 'ACCOUNT', 'DELETE', account, 'Delete user account', status.HTTP_204_NO_CONTENT)
            # Delete flow here [Task]
            alert = Alert.objects.create(
                account=Account.objects.filter(username='sysadmin').first(),
                code='delete_account_%s' % account.id,
                status=0,
                action_type=3
            )
            del_req.delete()
            task_delete_account.delay(alert_id=alert.id, account_id=account.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_410_GONE)


    @action(methods=['POST'], detail=False, url_path='request')
    def request_delete(self, request, *args, **kwargs):
        account = Account.objects.get(id=request.user.id)
        token = Account.delete_request(account)
        # sent email
        prefix = Config.pull_value('mailer-subject-prefix')
        header_image = Config.pull_value('mailer-header-image')
        icon_image = Config.pull_value('mailer-icon-image')
        subject = '%s - Your account has been canceled.' % prefix
        link = settings.CO2_WEB_URL + '/del_acc/%s' % token

        body = render_to_string(
            'mailer/account/confirm_delete_account_email.html',
            {
                'header_image': settings.CO2_API_URL + header_image,
                'mail_icon': settings.CO2_API_URL + icon_image,
                'link': link
            }
        )
        send_mail(account.email, subject, body, 1)

        return Response(status=status.HTTP_200_OK)


class AccountView(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    permission_classes = [IsAuthenticated,]
    serializer_class = AccountSerializer

    def create(self, request, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                return Response(data={'detail': 'You are not superuser'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            user = Account.objects.create(**request.data)
            password = generate_token(8)
            user.set_password(password)
            user.save()
            serializer = AccountSerializer(user)
            data = serializer.data.copy()
            data['password'] = password
            return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['GET'], detail=False, url_path='nftAccessToken')
    def nft_access_token(self, request, *args, **kwargs):
        try:
            token = UtilityToken.objects.get(
                account=request.user,
                name='nft_access_token'
            )
        except UtilityToken.DoesNotExist:
            headers = {
                'authorization': settings.CO2_NFT_API_KEY,
                'Content-Type': 'application/json'
            }

            payload = json.dumps({
                'account_id': request.user.id
            })

            response = requests.request(
                'POST',
                f'{settings.CO2_NFT_API_URL}jwt/get_token',
                headers=headers,
                data=payload
            )

            if response.status_code != 200:
                return Response(data={'detail': response.json()}, status=status.HTTP_406_NOT_ACCEPTABLE)

            token = UtilityToken.objects.create(
                account=request.user,
                name='nft_access_token',
                token=response.json().get('accessToken')
            )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'nftAccessToken': token.token}, status=status.HTTP_200_OK)
