import json

from django.conf import settings
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from datetime import datetime
from alert.models import Alert
from transaction.models import Transaction, Payment
from utils.SCB.scb_inquiry import scb_inquiry_data
from .models import SCBPayment
from .serializers import SCBPaymentConfirmationSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


class SCBPaymentConfirmationSerializerView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = SCBPayment.objects.all()
    serializer_class = SCBPaymentConfirmationSerializer
    permission_classes = (AllowAny,)

    permission_classes_action = {
        'create': [AllowAny],
    }

    action_serializers = {
        'create': SCBPaymentConfirmationSerializer
    }

    def get_serializer_class(self):
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]
        return super().get_serializer_class()


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        scb_confirmation = serializer.save()

        ### task for update about transaction data when SCB call out this task
        alert = Alert.objects.create(
            account_id=1,
            code='topup_transaction_%s' % scb_confirmation.transaction_id,
            status=0,
            action_type=4
        )
        transaction_date = datetime.now().strftime('%Y-%m-%d')

        event_code = settings.SCB_EVENT_CODE
        inquiry_data_dict = scb_inquiry_data(
            request,
            transaction_date,
            event_code,
            scb_confirmation.bill_payment_ref1,
            scb_confirmation.bill_payment_ref2,
            alert_id=alert.id
        )
        if not inquiry_data_dict:
            #Hard sent data request filter here
            alert.set_failed(traceback='Have someone try to use system in the wrong way')
            #TODO @Jade broadcast message to Admin here
        else:
            SCBPayment.complete_transaction(
                scb_pg_id=scb_confirmation.id,
                status_details=inquiry_data_dict['status']['description'],
                alert_id=alert.id
            )
        data_response = {
            "resCode": "00",
            "resDesc ": "success",
            "transactionId": scb_confirmation.transaction_id,
            "confirmId": scb_confirmation.id
        }
        return Response(data_response, status=status.HTTP_201_CREATED)
