from rest_framework import viewsets, status, mixins
from utils.response import Response
from utils.rest_framework.permissions import UnauthorizedPermission

from .serializers import NewsUpdateHomeSerializer
from .models import NewsUpdate


class NewsUpdatePinView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = NewsUpdate.objects.all()
    serializer_class = NewsUpdateHomeSerializer
    permission_classes = (UnauthorizedPermission,)

    def list(self, request, *args, **kwargs):
        news_update_list = NewsUpdate.pull_announcement()
        return Response({
            'results': self.get_serializer(news_update_list, many=True).data
        }, status=status.HTTP_200_OK)
