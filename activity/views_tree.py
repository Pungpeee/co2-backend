import json

import requests
from django.db.models import Sum, Count
# Create your views here.
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import Account
from alert.models import Alert
from co2 import settings
from log.models import Log
from utils.rest_framework.serializers import NoneSerializer
from .models import CarbonActivity
from .serializers import ActivityRecentSerializer
from .tree_activity_sync_tasks import task_sync_tree_data


class TreeActivityView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CarbonActivity.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = NoneSerializer

    permission_classes_action = {
        'list': [IsAuthenticated],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.account = Account.objects.filter(id=request.user.id).first()
        if self.account is None:
            raise NotFound

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = CarbonActivity.objects.filter(
            transaction__account_id=self.request.user.id,
            type=5,
            transaction__method=4
        )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = ActivityRecentSerializer(queryset, many=True).data
        return Response(data=response_data)
