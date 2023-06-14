import re

from django.http import Http404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from .models import SCBPayment

class SCBPaymentConfirmationSerializer(serializers.Serializer):
    payeeProxyId = serializers.CharField()
    payeeProxyType = serializers.CharField()
    payeeAccountNumber = serializers.CharField()
    payeeName = serializers.CharField()
    payerAccountNumber = serializers.CharField()
    payerAccountName = serializers.CharField()
    payerName = serializers.CharField()
    sendingBankCode = serializers.CharField()
    receivingBankCode = serializers.CharField()
    amount = serializers.CharField()
    transactionId = serializers.CharField()
    transactionDateandTime = serializers.CharField()
    billPaymentRef1 = serializers.CharField()
    billPaymentRef2 = serializers.CharField()
    billPaymentRef3 = serializers.CharField()
    currencyCode = serializers.CharField()
    channelCode = serializers.CharField()
    transactionType = serializers.CharField()

    def create(self, validated_data):
        SCB_payment = SCBPayment.objects.create(
            payee_proxy_id = validated_data['payeeProxyId'],
            payee_proxy_type = validated_data['payeeProxyType'],
            payee_name = validated_data['payeeName'],
            payee_account_number = validated_data['payeeAccountNumber'],
            payer_account_number = validated_data['payerAccountNumber'],
            payer_account_name = validated_data['payerAccountName'],
            payer_name = validated_data['payerName'],
            sending_bank_code = validated_data['sendingBankCode'],
            receiving_bank_code = validated_data['receivingBankCode'],
            amount = validated_data['amount'],
            transaction_id = validated_data['transactionId'],
            transaction_datetime = validated_data['transactionDateandTime'],
            bill_payment_ref1 = validated_data['billPaymentRef1'],
            bill_payment_ref2 = validated_data['billPaymentRef2'],
            bill_payment_ref3 = validated_data['billPaymentRef3'],
            currency_code = validated_data['currencyCode'],
            channel_code = validated_data['channelCode'],
            transaction_type = validated_data['transactionType']
        )
        return SCB_payment

