from rest_framework.filters import OrderingFilter
from utils.advanced_filters.emoji_filter import SearchFilter
from utils.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from utils.rest_framework.permissions import UnauthorizedPermission
from .caches import cache_news_update_pull_list
from .models import NewsUpdate
from .serializers import NewsUpdateDetailSerializer, NewsUpdateListSerializer


class NewsUpdateView(ReadOnlyModelViewSet):
    queryset = NewsUpdate.objects.filter(is_display=True).order_by('-is_pin', '-datetime_update')
    serializer_class = NewsUpdateListSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    ordering_fields = ('id',)
    filter_fields = ('is_pin',)
    search_fields = ('name',)
    permission_classes = (UnauthorizedPermission,)
    action_serializers = {
        'list': NewsUpdateListSerializer,
        'retrieve': NewsUpdateDetailSerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        queryset = cache_news_update_pull_list()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data).data
            count_unread = NewsUpdate.count_unread(request.user)
            response.update(count_unread)
            return Response(response)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = NewsUpdate.pull(kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
