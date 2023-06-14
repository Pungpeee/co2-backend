from rest_framework import viewsets

from account.models import Token
from utils.generator import generate_token
from rest_framework.response import Response
from utils.rest_framework.serializers import NoneSerializer


class TokenView(viewsets.GenericViewSet):
    queryset = Token.objects.none()
    serializer_class = NoneSerializer

    def list(self, request, *args, **kwargs):
        token = Token.objects.filter(account=request.user).first()
        if token is None:
            token = Token.objects.create(
                account=request.user,
                token=generate_token(32),
            )

        return Response({'token': token.token})
