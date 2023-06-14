import os

from azure.storage.blob import BlobServiceClient
from django.conf import settings
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notification_template.models import Trigger
from .caches import cached_account_profile, cache_account_delete
from .models import Account, KYCAccount, IdentityVerification
from .serializers import AccountSerializer, UserUpdateSerializer, UserUpdatePhotoKYCSerializer, UserAllSerializer, \
    KYCAccountSerializer
from config.models import Config
from utils.generator import generate_token
import json
import requests
from log.models import Log


class ProfileView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Account.objects.none()
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    permission_classes_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'profile_patch': [IsAuthenticated],
        'photo_KYC': [IsAuthenticated],
    }

    action_serializers = {
        'list': AccountSerializer,
        'retrieve': AccountSerializer,
        'profile_patch': AccountSerializer,
        'photo_KYC': UserUpdatePhotoKYCSerializer
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Account.objects.filter(id=self.request.user.id)
        else:
            return self.queryset

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def get_object(self, queryset=None):
        account = Account.objects.filter(pk=self.request.user.id).first()
        return account

    def list(self, request, *args, **kwargs):
        # is already has wallet?
        account = request.user
        if not account.sol_public_key and not account.bsc_public_key:
            headers = {
                'authorization': settings.CO2_CHAIN_API_KEY,
                'Content-Type': 'application/json'
            }
            url = settings.CO2_CHAIN_API_URL + 'wallet/create_wallet'
            payload = json.dumps({
                'account_id': account.id,
                'mcard': False
            })

            response = requests.request(
                'POST',
                url,
                headers=headers,
                data=payload
            )

            if response.status_code != 200 or response.status_code != 201:
                Log.push(request, 'ACCOUNT', 'CREATE_WALLET', account,
                         'Have something wrong with API create wallet',
                         status.HTTP_200_OK, payload=response.__dict__)

            wallet_data = json.loads(response.text)
            if not wallet_data.get('public_key', None):
                Log.push(request, 'ACCOUNT', 'CREATE_WALLET', account,
                         'Have something wrong with API create wallet',
                         status.HTTP_200_OK, payload=response.__dict__)
            else:
                public_key = wallet_data.get('public_key', None)
                account.sol_public_key = public_key.get('sol', None)
                account.bsc_public_key = public_key.get('bsc', None)
            account.save()
        return Response(cached_account_profile(request.user.id))

    def profile_patch(self, request, *args, **kwargs):
        account = self.get_object()

        # phone = account.phone
        serializer = UserUpdateSerializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # data = serializer.validated_data
        # if data and data.get('phone') and phone is not data.get('phone'):
        #     kyc_account = KYCAccount.objects.filter(account_id=account.id).first()
        #     kyc_account.is_mobile_verify=False
        #     kyc_account.save(update_fields=['is_mobile_verify'])

        serializer.save()
        # identify = None
        # if data and data.get('phone', None):
        #     identify = IdentityVerification.send_verification(account.id, 2, 2)  # Send OTP Verification
        # cache_account_delete(account.id)
        data = self.get_serializer(self.get_object()).data
        # if identify:
        #     data.update({'otp_ref_code': identify.ref_code})
        return Response(data=data)

    @action(methods=['POST'], detail=False, url_path='photo_KYC')
    def photo_KYC(self, request, *args, **kwargs):
        account = self.get_object()
        # TODO Fix this flow after done with #2pj76k4
        account_kyc = KYCAccount.objects.filter(account_id=request.user.id).first()
        serializers = self.get_serializer(account_kyc, data=request.data, partial=True)
        ####################################################################################
        serializers.is_valid(raise_exception=True)
        serializers.save()
        Account.send_email_kyc(email=account.email, status=2)
        trigger = Trigger.get_code('kyc_pending')
        trigger.send_notification(
            sender=None,
            inbox_type=1,
            inbox_content_type=settings.CONTENT_TYPE('account.account'),
            inbox_content_id=account.id,
            account_list=[account]
        )
        return Response(serializers.data, status=status.HTTP_200_OK)

    @action(methods=['PATCH'], detail=False, url_path='updateEmail')
    def update_email(self, request, *args, **kwargs):
        account = self.get_object()
        if account.email:
            return Response(data={'detail': 'This account already has email'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        if not data.get('email', None):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = UserAllSerializer(account, data={
            'email': data['email']
        }, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        account = serializer.save()

        if not account.code:
            while True:
                token = generate_token(32)
                if not Account.objects.filter(code=token).exists():
                    break
            account.code = token
            account.save()

        site_url = Config.pull_value('config-site-url-app-link')
        Account.create_verify_email(
            email=account.email,
            token=account.code,
            site_url=site_url
        )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='kyc')
    def get_kyc(self, request, *args, **kwargs):
        user = request.user
        account = Account.objects.get(pk=user.id)
        try:
            kyc = KYCAccount.objects.get(account=account)
            serializer = KYCAccountSerializer(kyc)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except KYCAccount.DoesNotExist:
            kyc = KYCAccount.objects.create(
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
            serializer = KYCAccountSerializer(kyc)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, url_path='kyc-update')
    def create_kyc(self, request, *args, **kwargs):
        user = request.user
        account = Account.objects.get(pk=user.id)
        try:
            kyc = KYCAccount.objects.get(account=account)
            serializer = KYCAccountSerializer(kyc, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            kyc = serializer.save()
            return Response(data=KYCAccountSerializer(kyc).data, status=status.HTTP_201_CREATED)
        except KYCAccount.DoesNotExist:
            return Response(data={'error': 'Please get kyc first'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
