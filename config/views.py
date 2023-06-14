from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from config.models import Config
from config.serializers import ConfigSerializer


class FeatureView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Config.objects.none()
    serializer_class = ConfigSerializer
    allow_redirects = True
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        list_configs = ['config-carbon-saving-is-enabled']
        data_dict = {}
        for config in list_configs:
            data_dict.update({config: Config.pull_value(config)})
        return Response(data=data_dict)

    # @action(methods=['GET'], detail=False, url_path='version')
    # def version_get(self, request, *args, **kwargs):
    #     return Response(data={'version': Config.pull_value('version')})

    @action(methods=['POST'], detail=False, url_path='version')
    def version_post(self, request, *args, **kwargs):
        # { "version": "carbonwallet1.1.0" }
        client_version = request.data.get('version', '').replace('carbonwallet', '').split('.')
        current_version = Config.pull_value('version').split('.')
        force_update_version = ''
        try:
            force_update_version = Config.pull_value('force_update_version').split('.')
        except Exception as e:
            force_update_version = client_version
        has_new = False
        force_update = False
        full_client_version = ''
        full_current_version = ''
        full_force_update_version = ''
        for i in range(len(client_version)):
            full_client_version += client_version[i]
            full_current_version += current_version[i]
            full_force_update_version += force_update_version[i]
        if int(full_client_version) <= int(full_current_version):
            has_new = True
        if int(full_client_version) <= int(full_force_update_version):
            force_update = True

        data = {
            'allow_use': force_update,
            'has_new_version': has_new
        }
        return Response(data=data)
