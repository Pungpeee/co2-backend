from django.conf import settings

from rest_framework import mixins, viewsets, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from utils.advanced_filters.emoji_filter import SearchFilter

from inbox.caches import cache_account_count_delete
from inbox.models import Inbox
from .serializers import InboxReadSerializer, InboxSerializer


class InboxView(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Inbox.objects.filter(status=1)
    serializer_class = InboxSerializer
    filter_backends = (OrderingFilter, SearchFilter)
    ordering_fields = ('title', 'id')
    search_fields = ('title', 'id')

    action_serializers = {
        'create': InboxReadSerializer,  # Create Read ann mark content is_read = True
        'list': InboxSerializer,
    }

    def get_queryset(self):
        return self.queryset.filter(member__account=self.request.user)

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer_list = []

        page_queryset = self.paginate_queryset(queryset)
        context = self.get_serializer_context()

        for inbox in page_queryset:
                serializer_list.append(self.get_serializer(inbox, context=context).data)

        response = self.get_paginated_response(serializer_list).data
        return Response(response)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        cache_account_count_delete(request.user.id)
        return Response(status=status.HTTP_201_CREATED, headers=headers)
