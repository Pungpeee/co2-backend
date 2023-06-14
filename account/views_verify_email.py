from django.shortcuts import render
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Account
from .serializers import AccountVerifyEmailSerializer


class VerifyEmailView(viewsets.GenericViewSet):
    queryset = Account.objects.none()
    serializer_class = AccountVerifyEmailSerializer
    permission_classes = (AllowAny,)

    app = 'account'
    model = 'account'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.token = request.GET.get('token')
        if self.token is None:
            raise NotFound

    def list(self, request, *args, **kwargs):
        if not self.token:
            return Response(data={'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        account = Account.objects.filter(code=self.token).first()
        if account is None:
            # return Response(data={'Have no this token in system'}, status=status.HTTP_404_NOT_FOUND)
            return render(
                request,
                'verify_email_success.html',
                {}
            )

        account.is_active = True
        account.is_verified_email = True
        account.code = None

        account.save(update_fields=['code', 'is_active', 'is_verified_email', 'datetime_update'])
        # return Response(AccountVerifyEmailSerializer(account).data, status=status.HTTP_201_CREATED)
        return render(
            request,
            'verify_email_success.html',
            {}
        )
    @action(methods=['GET'], detail=False, url_path='(?P<token>[a-zA-Z0-9]+)')
    def check(self, request, *args, **kwargs):
        token = kwargs.get('token')
        account = Account.objects.filter(code=token).first()
        if account is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif not account.is_active:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not account.is_verified_email:
            return Response(data={"Reason": "This account is not verify email yet"}, status=status.HTTP_423_LOCKED)
        else:
            return Response({'detail': 'Valid token'}, status=status.HTTP_200_OK)
