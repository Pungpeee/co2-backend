from django.utils import timezone
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Mailer
from .tasks import send_mail
from .serializers import MailerSerializer


class MailerView(viewsets.GenericViewSet):
    queryset = Mailer.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = MailerSerializer

    @action(['POST'], detail=False, url_path='contact')
    def contact(self, request, *args, **kwargs):
        data = request.data
        if not data.get('subject', None) and not data.get('body', None):
            return Response(data={'detail': 'All input Is required'}, status=status.HTTP_400_BAD_REQUEST)
        send_mail('contact@vekin.co.th', data['subject'], data['body'], 5)
        return Response(status=status.HTTP_200_OK)
