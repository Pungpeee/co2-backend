from rest_framework import viewsets
from rest_framework.response import Response

from inbox.caches import cache_account_count
from inbox.models import Inbox
from .serializers import CountSerializer


class NotificationStatusView(viewsets.GenericViewSet):
    queryset = Inbox.objects.none()
    serializer_class = CountSerializer

    def get_queryset(self):
        return self.queryset

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            count = cache_account_count(request.user).count
        else:
            count = 0
        response = {
            'count': count
        }
        return Response(response)
