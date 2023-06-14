from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import Account
from alert.models import Alert
from config.models import Config
from transaction.models import Transaction
from transaction.serializers import TransactionSerializer, TransactionSwapReceiver


class TransactionSwapView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSwapReceiver
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    permission_classes_action = {
        'create': [IsAuthenticated]
    }

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
        serializer = TransactionSwapReceiver(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        sol_amount = data['sol_amount']
        account = Account.objects.filter(id=self.request.user.id, is_active=True).first()
        if not account:
            return Response(data={'Have no this account is activated on any systems'}, status=status.HTTP_404_NOT_FOUND)

        config_wap_feature = Config.pull_value('config-swap-enable')
        if not config_wap_feature:
            return Response(data={'This feature unavailable'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        alert = Alert.objects.create(
            account_id=account.id,
            code='swap_sol_coin_account_%s' % account.id,
            status=0,
            action_type=3
        )
        if Transaction.objects.filter(account_id=account.id, status__in=[1]).exists():
            return Response(
                data={"Details: This account already have Top-up transaction pending, Please Finish them first"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            transaction = Transaction.objects.create(
                account_id=account.id,
                desc='swap coin',
                source_key=account.sol_public_key,
                destination_key=account.bsc_public_key,
                values=float(sol_amount) if sol_amount or sol_amount >= 0.0 else 0.0,
                coin=1,
                method=6,
                status=-1,
                datetime_start=timezone.now()
            )

        from .transaction_swap_token_tasks import task_transaction_swap_token
        task_transaction_swap_token.delay(transaction_id=transaction.id, alert_id=alert.id)
        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

