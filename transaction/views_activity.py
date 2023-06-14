
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activity.models import CarbonActivity
from co2 import settings
from log.models import Log
from .models import Transaction
from .serializers import TransactionSerializer, TransactionActivityCreateSerializer


class TransactionActivityView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionSerializer

    permission_classes_action = {
        'create': [IsAuthenticated]
    }

    action_serializers = {
        'create': TransactionActivityCreateSerializer,
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Transaction.objects.filter(account_id=self.request.user.id)
        else:
            return self.queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        transaction = serializer.save()

        print('validate data of activity create', data)

        activity = CarbonActivity.objects.create(
            transaction_id=transaction.id,
            type=data.get('activity_type'),
            desc=data.get('desc'),
            carbon_saving=data.get('values')
        )
        

        Log.push(
            None, 'TRANSACTION', 'CREATE', self.request.user, 'Create transaction activity', status.HTTP_201_CREATED,
            content_type=settings.CONTENT_TYPE('transaction.transaction'), content_id=transaction.id,
        )
