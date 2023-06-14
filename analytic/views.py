from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from config.models import Config
from utils.ip import get_client_ip
from .models import Session
from .serializers import SessionSerializer


class SessionView(mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)

    ordering_fields = ('datetime_create',)
    filter_fields = ('account', 'source', 'ip', 'datetime_create')

    app = 'analytic'
    model = 'session'

    def create(self, request, *args, **kwargs):
        is_session_enable = Config.pull_value('config-session-analytic-enabled')
        if not is_session_enable:
            return Response({}, status=status.HTTP_201_CREATED)
        """
        Parameters:
        - SOURCE = (
                (-1, _('(Not set)')),
                (0, _('Web')),
                (1, _('Mobile')),
                (2, _('Tablet')),
            )
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'status': 'OK'}, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        Session.push_redis(self.request, serializer.validated_data.get('source', 0))
