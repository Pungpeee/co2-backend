from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import CarbonActivity
from .serializers import ActivitySerializer


class PartnerView(viewsets.GenericViewSet):
    queryset = CarbonActivity.objects.all()
    allow_redirects = True
    permission_classes = (AllowAny,)
    serializer_class = ActivitySerializer

    @action(methods=['GET'], detail=False, url_path='draft-activity/(?P<key>[A-Za-z0-9]+)')
    def g(self, request, *args, **kwargs):
        if kwargs.get('key', '') != settings.CERO_OCR_INTERNAL_API_KEY:
            return Response(data={'detail': 'Wrong api-key'}, status=status.HTTP_403_FORBIDDEN)

        # TODO:
        # request.data
        # CarbonActivity.objects.create()

        return Response(data={}, status=status.HTTP_200_OK)
