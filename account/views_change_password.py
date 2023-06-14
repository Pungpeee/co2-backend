from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from account.serializers_change_password import ChangePasswordSerializer


class ChangePasswordViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)
