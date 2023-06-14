from django.utils import timezone
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from account.serializers_reset_password import ResetPasswordSerializer
from log.models import Log
from rest_framework.response import Response
from .models import Forgot


class ResetPasswordView(viewsets.GenericViewSet):
    queryset = Forgot.objects.none()
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data['new_password'] != data['confirm_password']:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        forgot = Forgot.objects.filter(token=data['token'], method=data['method']).first()

        if forgot is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif forgot.status == -1 or forgot.is_token_expire:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            if not forgot.account.is_active:
                return Response(status=status.HTTP_404_NOT_FOUND)

        Log.push(request, 'ACCOUNT', 'RESET_PASSWORD', forgot.account, 'User password ', status.HTTP_200_OK)
        forgot.account.last_active = timezone.now()
        forgot.account.save()

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=False, url_path='(?P<token>[a-zA-Z0-9]+)')
    def check(self, request, *args, **kwargs):
        token = kwargs.get('token')
        forgot = Forgot.objects.filter(token=token).first()
        if forgot is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif forgot.status == -1:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        elif forgot.status == 2:
            return Response(status=status.HTTP_423_LOCKED)
        else:
            return Response({'detail': 'Valid token'}, status=status.HTTP_200_OK)
