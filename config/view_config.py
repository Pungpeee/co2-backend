from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config.models import Config
from utils.rest_framework.serializers import NoneSerializer


class FeatureView(viewsets.GenericViewSet):
    queryset = Config.objects.none()
    serializer_class = NoneSerializer
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        list_configs = ['config-carbon-saving-is-enabled']
        queryset = Config.objacts.all()
        data_dict = {}
        for config in list_configs:
            data_dict.update({config: Config.pull_value(config)})
        return Response(data=data_dict)





