from django.conf import settings
from django.db.models import F
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from account.models import Account
from inbox.caches import cache_account_count_delete
from log.models import Log
from utils.advanced_filters.emoji_filter import SearchFilter

from inbox.models import Inbox, Member
from inbox.serializers import InboxReadSerializer, InboxSerilailizer


class InboxView(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                mixins.DestroyModelMixin,
                viewsets.GenericViewSet):
    queryset = Inbox.objects.all()
    serializer_class = InboxSerilailizer
    filter_backends = (OrderingFilter, SearchFilter)

    ordering_fields = ('title', 'id')
    search_fields = ('title', 'id')

    action_serializers = {
        'list': InboxSerilailizer,
        'mark_all_read': InboxSerilailizer,
        'create': InboxReadSerializer,  # Create Read and mark is_read = True,
    }

    def get_queryset(self):
        inbox_id_list = Member.objects.filter(
            inbox__status=1,
            account_id=self.request.user.id
        ).values_list('inbox_id', flat=True)
        return self.queryset.filter(status=1, id__in=inbox_id_list)

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer_list = []

        page_queryset = self.paginate_queryset(queryset)
        for inbox in page_queryset:
            serializer_list.append(self.get_serializer(inbox).data)
        response = self.get_paginated_response(serializer_list).data
        return Response(response)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        cache_account_count_delete(request.user.id)
        return Response(status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['GET'], detail=False, url_path='mark_all_read')
    def mark_all_read(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(count_read=0))
        for inbox in queryset:
            if not inbox.read_set.filter(account_id=self.request.user.id).exists():
                inbox.read_set.create(account_id=self.request.user.id)
        queryset = queryset.update(count_read=F('count_read')+1)
        return Response(data={'Mark all as read %s inbox' % queryset}, status=status.HTTP_200_OK)

    @action(methods=['DELETE'], detail=False, url_path='multiple_delete')
    def multiple_delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        Log.push(
            None, 'Inbox', 'DELETE', request.user, 'Delete all inbox', status.HTTP_204_NO_CONTENT,
            content_type=settings.CONTENT_TYPE('inbox.inbox'), content_id=-1,
            note='inbox/views.py multiple_delete()'
        )
        return Response(status=status.HTTP_204_NO_CONTENT)