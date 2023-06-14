from django.utils import timezone
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer, TransactionUpdateStatusSerializer, TransactionPaymentSerializer


class TransactionView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionSerializer
    filter_fields = ('account', 'coin', 'method', 'status')
    search_fields = ('account', 'coin', 'method', 'status')

    permission_classes_action = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
    }

    action_serializers = {
        'list': TransactionSerializer,
        'retrieve': TransactionPaymentSerializer,
        'partial_update': TransactionUpdateStatusSerializer,
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
        else:
            response_data = self.get_serializer(queryset, many=True).data
        return Response(data=response_data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        transaction = self.get_object()
        if transaction.status in [-3, -2, 2]:
            return Response(data={'This transaction can not update anymore'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = TransactionUpdateStatusSerializer(transaction, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        status_update = serializer.validated_data.get('status', None)
        if status_update and int(status_update) == -2:
            serializer.validated_data.update({'datetime_cancel': timezone.now()})
        serializer.save()
        return Response(TransactionSerializer(transaction).data)



