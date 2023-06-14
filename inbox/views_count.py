from rest_framework import status, viewsets, mixins
from rest_framework.response import Response

from inbox.caches import cache_account_count, cache_account_count_unread
from inbox.models import Count, Inbox
from .serializers import CountSerializer, ReadCountSerializer


class CountUnreadViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Inbox.objects.none()
    serializer_class = CountSerializer

    def get_queryset(self):
        return self.queryset

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            count_unread = cache_account_count_unread(request.user)
        else:
            count_unread = 0
        response = {
            'count': count_unread
        }
        return Response(data=response, status=status.HTTP_200_OK)


class ReadCountViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Count.objects.none()
    serializer_class = ReadCountSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def perform_create(self, serializer):
        count = cache_account_count(self.request.user)
        if count.count > 0:
            count.clear_count()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_200_OK, headers=headers)
