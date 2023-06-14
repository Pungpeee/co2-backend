from django.utils import timezone
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Event
from .serializers import EventSerializer


class EventView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    queryset = Event.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = EventSerializer

    permission_classes_action = {
        'list': [IsAuthenticated],
        'create': [IsAdminUser],
        'partial_update': [IsAdminUser]
    }

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(is_active=True)
        response_data = self.get_serializer(queryset, many=True).data
        return Response(data=response_data)
