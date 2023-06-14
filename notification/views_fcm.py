from fcm_django.api.rest_framework import AuthorizedMixin
from fcm_django.models import FCMDevice
from rest_framework import mixins, viewsets

from notification.serializers import FCMDeviceSerializer
from utils.content import fcm_notification_config


class DeviceViewSetMixin(object):
    lookup_field = "registration_id"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        if (self._setting['ONE_DEVICE_PER_USER'] and
                self.request.data.get('active', True)):
            FCMDevice.objects.filter(user=self.request.user).update(
                active=False)

        return super(DeviceViewSetMixin, self).perform_create(serializer)

    @property
    def _setting(self):
        fcm_settings = fcm_notification_config().get('fcm_django', None)
        if fcm_settings:
            return fcm_settings.get('setting', None)
        else:
            return {"ONE_DEVICE_PER_USER": True}


class FCMView(DeviceViewSetMixin, mixins.CreateModelMixin, AuthorizedMixin, viewsets.GenericViewSet):
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
