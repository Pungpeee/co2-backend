from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import Account
from log.models import Log
from notification_template.models import Trigger
from transaction.models import Transaction, Payment
from transaction.serializers import TransactionTopUp, TransactionSerializer, TransactionPaymentSerializer


class TransactionTopUpView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    permission_classes_action = {
        'create': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        # 'upload_payslip': [IsAuthenticated],
    }

    action_serializers = {
        'create': TransactionTopUp,
        'retrieve': TransactionPaymentSerializer,
        # 'upload_payslip': PaymentUpdatePaySlip,
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

        if not data.get('token_name', None):
            return Response(data='Token name is required', status=status.HTTP_400_BAD_REQUEST)

        token_name = data.get('token_name', None)
        if not token_name or token_name not in ['GREEN', 'CERO']:
            return Response(data='Have no this token name in system', status=status.HTTP_404_NOT_FOUND)

        if not data.get('is_own_account') or not data.get('is_not_reuse') or not data.get('is_not_overtime'):
            return Response(data='User not accept condition', status=status.HTTP_405_METHOD_NOT_ALLOWED)

        account = Account.objects.filter(id=request.user.id).first()
        if not account:
            Log.push(request, 'ACCOUNT',
                     'TOP_UP', account, 'Have something wrong with API top up',
                     status.HTTP_200_OK)
            return Response(data={'Details : This account have no in system'}, status=status.HTTP_404_NOT_FOUND)

        thb_amount = data.get('thb_amount', None)
        if not thb_amount or float(thb_amount) <= 0.00000000001:
            Log.push(request, 'ACCOUNT',
                     'TOP_UP', account, 'Have something wrong with API top up',
                     status.HTTP_200_OK)
            return Response(
                data={'Details : THB Amount is require and THB amount must more then 0.00000000001'},
                status=status.HTTP_400_BAD_REQUEST
            )

        coin_amount = data.get('coin_amount', None)
        if not coin_amount or float(coin_amount) <= 0.00000000001:
            Log.push(request, 'ACCOUNT',
                     'TOP_UP', account, 'Have something wrong with API top up',
                     status.HTTP_200_OK)
            return Response(
                data={'Details : Coin Amount is require and Coin amount must more then 0.00000000001'},
                status=status.HTTP_400_BAD_REQUEST
            )
        token_name = token_name.upper()

        # TODO : Remove this in future that can buy another coin
        if token_name != "CERO":
            return Response(data='This Token not allow to buy yet, Please Contact admin.',
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        coin = [item for item in Transaction.COIN_CHOICES if item[1] == token_name]
        if not coin or not coin[0][0]:
            return Response(data='Have no this token name in system', status=status.HTTP_404_NOT_FOUND)

        if Transaction.objects.filter(account_id=account.id, status__in=[1]).exists():
            return Response(
                data={"Details: This account already have Top-up transaction pending, Please Finish them first"},
                status=status.HTTP_400_BAD_REQUEST
            )

        transaction = Transaction.objects.create(
            account_id=account.id,
            transaction_hash='',
            source_key='',
            paid_by=account.get_full_name(),
            destination_key=account.sol_public_key,
            values=coin_amount,
            thb_values=thb_amount,
            coin=coin[0][0],
            method=3,
            status=1,
            datetime_start=timezone.now()
        )

        payment = Payment.objects.create(
            transaction_id=transaction.id,
        )

        trigger = Trigger.get_code('top_up')
        trigger.send_notification(
            sender=None,
            inbox_type=1,
            inbox_content_type=settings.CONTENT_TYPE('transaction.transaction'),
            inbox_content_id=transaction.id,
            account_list=[transaction.account]
        )

        # Gen QRCODE for payment
        from utils.SCB.gen_qr_payment import gen_qr_payment
        qr_payment = gen_qr_payment(request, transaction.id, payment.id, transaction.thb_values)
        if not qr_payment:
            return Response(data='SCB Payment Gateway can\'t Generate QRCODE', status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction.pull(transaction.id)
        serializer = TransactionPaymentSerializer(transaction).data
        return Response(serializer, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # @action(methods=['POST'], detail=False, url_path='upload_payslip/(?P<transaction_id>[0-9]+)')
    # def upload_payslip(self, request, *args, **kwargs):
    #     transaction_id = kwargs.get('transaction_id', -1)
    #     transaction = Transaction.objects.filter(id=transaction_id).first()
    #
    #     if not transaction:
    #         return Response(data={'Details : Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)
    #
    #     payment = transaction.payment_set.order_by('-datetime_create')
    #
    #     if payment.count() > 1:
    #         Log.push(request, 'TRANSACTION',
    #                  'PAYMENT_PENDING', transaction,
    #                  'transaction id %s have payment object more that one',
    #                  status.HTTP_409_CONFLICT)
    #
    #     payment = transaction.payment_set.order_by('-datetime_create').first()
    #
    #     serializers = PaymentUpdatePaySlip(payment, data=request.data, partial=True)
    #     serializers.is_valid(raise_exception=True)
    #     serializers.save()
    #     if serializers.data.get('payment_slip', None):
    #         transaction.status = -1
    #         transaction.save(update_fields=['status', 'datetime_update'])
    #         Transaction.send_topup_noti(transaction_id=transaction.id, topup_status=-1)
    #         trigger = Trigger.get_code('top_up')
    #         trigger.send_notification(
    #             sender=None,
    #             inbox_type=1,
    #             inbox_content_type=settings.CONTENT_TYPE('transaction.transaction'),
    #             inbox_content_id=transaction.id,
    #             account_list=[transaction.account]
    #         )
    #     return Response(serializers.data, status=status.HTTP_200_OK)

