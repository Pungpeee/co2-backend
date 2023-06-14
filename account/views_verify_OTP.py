from django.shortcuts import render
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from log.models import Log
from .caches import cache_account_delete
from .models import Account, IdentityVerification, KYCAccount
from .serializers import AccountVerifyEmailSerializer


class VerifyMobileOTPView(viewsets.GenericViewSet):
    queryset = Account.objects.none()
    serializer_class = AccountVerifyEmailSerializer
    permission_classes = (IsAuthenticated,)

    app = 'account'
    model = 'identity'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.account = Account.objects.get(id=self.request.user.id)
        if self.account is None:
            raise NotFound

    @action(methods=['GET'], detail=False, url_path='OTPVerification/(?P<token>\w+)')
    def otp_verification(self, request, *args, **kwargs):
        token = self.kwargs.get('token')
        if not token:
            Log.push(
                request, 'ACCOUNT', 'CONFIRM_OTP', request.user,
                'Have no token in request', status.HTTP_400_BAD_REQUEST
            )
            return Response(data={'result': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        account = Account.objects.get(id=request.user.id)
        kyc_account = KYCAccount.objects.filter(account_id=account.id).first()
        identify = IdentityVerification.objects.filter(
            method=2, send_method=2, account_id=request.user.id, token=token, status=1
        ).first()
        if identify:
            identify.status = -1
            identify.save(update_fields=['status'])
            kyc_account.is_mobile_verify = True
            kyc_account.save(update_fields=['is_mobile_verify'])
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)