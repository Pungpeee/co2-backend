from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from config.models import Config
from transaction.models import Transaction, Payment
from utils.rest_framework.serializers import Base64ImageField


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionBalance(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id',
            'account',
            'desc',
            'method',
            'coin',
            'status',
            'values',
            'thb_values',
            'rate_per_usdt',
            'datetime_create'
        )

class TransactionRetrieveSearializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id',
            'account',
            'transaction_hash',
            'source_key',
            'destination_key',
            'values',
            'thb_values',
            'paid_by',
            'coin',
            'method',
            'status',
            'datetime_update',
            'datetime_complete'
        )

class PaymentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class TransactionPaymentSerializer(serializers.ModelSerializer):
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            'id',
            'desc',
            'method',
            'coin',
            'status',
            'values',
            'thb_values',
            'rate_per_usdt',
            'datetime_create',
            'payment'
        )

    def get_payment(self, transaction):
        from transaction.models import Payment
        payment = Payment.objects.filter(transaction_id=transaction.id).first()
        return PaymentResultSerializer(payment).data


class TransactionTopUp(serializers.Serializer):
    token_name = serializers.CharField(required=True)
    thb_amount = serializers.FloatField(required=True)
    coin_amount = serializers.FloatField(required=True)
    is_own_account = serializers.BooleanField(default=False)
    is_not_reuse = serializers.BooleanField(default=False)
    is_not_overtime = serializers.BooleanField(default=False)


class PaymentUpdatePaySlip(serializers.ModelSerializer):
    payment_slip = Base64ImageField(allow_empty_file=True, allow_null=True, required=True)
    datetime_stamp = serializers.DateTimeField(required=True)

    class Meta:
        model = Payment
        fields = (
            'id',
            'payment_slip',
            'datetime_stamp'
        )

    def update(self, payment, validated_data):
        if 'payment_slip' in validated_data:
            if validated_data['payment_slip']:
                validated_data['payment_slip_log'] = validated_data['payment_slip']
        payment.datetime_stamp = timezone.now()
        payment.save()
        return super().update(payment, validated_data)


class TransactionActivityCreateSerializer(serializers.Serializer):
    account = serializers.SerializerMethodField()
    source_key = serializers.SerializerMethodField()
    destination_key = serializers.SerializerMethodField()
    values = serializers.SerializerMethodField()
    thb_values = serializers.SerializerMethodField()
    paid_by = serializers.SerializerMethodField()
    coin = serializers.SerializerMethodField()
    method = serializers.SerializerMethodField()
    activity_type = serializers.IntegerField()
    desc = serializers.CharField()
    code = serializers.CharField()

    class Meta:
        model = Transaction
        fields = (
            'id',
            'account',
            'source_key',
            'destination_key',
            'method',
            'coin',
            'status',
            'values',
            'thb_values',
            'rate_per_usdt',
            'datetime_create',
            'datetime_update',
            'activity_type',
            'desc',
            'code'
        )

    def create(self, validated_data):
        from account.models import Account
        from activity.models import CarbonActivity
        if 'account' in validated_data and not validated_data['account']:
            raise ValidationError('account is invalid.')
        is_account = Account.objects.filter(id=validated_data.get('account'), is_active=True).exists()
        if not is_account:
            raise ValidationError('account is invalid.')

        if 'method' in validated_data and not validated_data['method']:
            raise ValidationError('account is invalid.')

        method = validated_data.get('method')
        if method and not isinstance(method, int):
            raise ValidationError('method is invalid.')

        if int(method) != 4:
            raise ValidationError('method is match with type.')

        if 'activity_type' in validated_data and not validated_data['activity_type']:
            raise ValidationError('Activity type is invalid.')

        activity_type = validated_data.get('activity_type')
        if activity_type and not isinstance(activity_type, int):
            raise ValidationError('Activity type is invalid.')

        if int(activity_type) not in CarbonActivity.TYPE_CHOICE:
            raise ValidationError('method is match with type.')
        return super().create(validated_data)


class TransactionUpdateStatusSerializer(serializers.ModelSerializer):
    status = serializers.IntegerField(default=0)
    desc = serializers.CharField()

    class Meta:
        model = Transaction
        fields = (
            'id',
            'status',
            'desc'
        )

    def update(self, transaction, validated_data):
        from transaction.models import Payment
        if 'status' in validated_data:
            # upload new avatar
            if not validated_data['status']:
                raise ValidationError('status is required.')
            if not isinstance(validated_data['status'], int):
                raise ValidationError('Wrong format type status.')
            if int(validated_data['status']) not in dict(Transaction.STATUS_CHOICES):
                raise ValidationError('Status not match with status in system.')
            if int(validated_data['status']) == 2:
                payment_transaction = Payment.objects.filter(transaction_id=transaction.id).first()
                if not payment_transaction.payment_slip:
                    raise ValidationError(
                        'This transaction can not complete, because payment of this transaction does not pay.'
                    )
        return super().update(transaction, validated_data)

class TransactionSwapReceiver(serializers.Serializer):
    sol_amount = serializers.FloatField(required=True)




