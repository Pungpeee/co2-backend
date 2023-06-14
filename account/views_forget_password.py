from django.conf import settings
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from mailer.template_generator import ForgetPasswordUser
from .models import Account, Forgot
from .serializers import ForgetPasswordSerializer, check_email


class ForgetPasswordView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ForgetPasswordSerializer
    allow_redirects = True
    queryset = Account.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if not check_email(data['email']):
            return Response({'status': 'error_email_format'})

        account = Account.objects.filter(email=data['email']).first()
        if account is None:
            return Response({'status': 'error_email_not_found'})

        if not account.is_active:
            return Response({'status': 'error_account_inactive'})

        if account.is_force_reset_password:
            account.is_force_reset_password = False
            account.save(update_fields=['is_force_reset_password'])

        Forgot.objects.filter(account=account, method=1, status=1).update(status=-1)
        token = account.forgot_password()
        site_url = settings.CO2_WEB_URL
        full_name = account.get_full_name()
        ForgetPasswordUser.create_forget_user_password(full_name, data['email'], token, site_url, method=1)
        return Response({'status': 'success'})
