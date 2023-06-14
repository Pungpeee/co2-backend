from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Account
from .serializers import AccountPartnerSerializer


class PartnerView(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    allow_redirects = True
    permission_classes = (AllowAny,)
    serializer_class = AccountPartnerSerializer

    @action(methods=['GET'], detail=False, url_path='users/(?P<key>[A-Za-z0-9]+)')
    def g(self, request, *args, **kwargs):
        if kwargs.get('key', '') != settings.CERO_CMS_INTERNAL_API_KEY:
            return Response(data={'detail': 'Wrong api-key'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
