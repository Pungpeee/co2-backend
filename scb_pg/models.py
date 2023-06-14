from django.db import models

'''
transactionId, amount, transactionDateandTime, currencyCode, transactionType, 
merchantId, terminalId, qrID, merchantPAN, consumerPAN,
 traceNo, authorizeCode, payeeProxyType, payeeProxyId, payeeAccountNumber,
payeeName, payerProxyId, payerProxyType, payerName, payerAccountName, 
payerAccountNumber, billPaymentRef1, billPaymentRef2, billPaymentRef3, sendingBankCode, 
receivingBankCode, channelCode, paymentMethod, tenor, ippType,
productCode, exchangeRate, equivalentAmount, equivalentCurrencyCode, companyId, 
invoice, note
'''

class SCBPayment(models.Model):
    transaction_id = models.CharField(max_length=255, blank=True, null=True, default=None) # QR30
    amount = models.CharField(max_length=255, blank=True, null=True, default=None) # QR30
    transaction_datetime = models.CharField(max_length=255, blank=True, null=True, default=None) # QR30
    currency_code = models.CharField(max_length=255, blank=True, null=True, default=None) # QR30
    transaction_type = models.CharField(max_length=255, blank=True, null=True, default=None) # QR30
    # merchant_id = models.CharField(max_length=200, blank=True, null=True, default=None)
    # qr_id = models.TextField(blank=True)
    # merchant_pan = models.CharField(max_length=32, blank=True, null=True, default=None)
    # consumer_pan = models.CharField(max_length=32, blank=True, null=True, default=None)
    # trace_no = models.CharField(max_length=200, blank=True, null=True, default=None)
    # authorize_code = models.CharField(max_length=200, blank=True, null=True, default=None)
    payee_proxy_type =  models.CharField(max_length=255, blank=True, null=True, default=None) # QR30
    payee_proxy_id = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    payee_account_number = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    payee_name = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    payer_proxy_id = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    payer_proxy_type = models.CharField(max_length=255, blank=True, null=True, default=None) # QR30
    payer_name = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    payer_account_name = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    payer_account_number = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    bill_payment_ref1 = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    bill_payment_ref2 = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    bill_payment_ref3 = models.CharField(max_length=200, blank=True, null=True, default=None) # QR30
    sending_bank_code = models.CharField(max_length=10, blank=True, null=True, default=None) # QR30
    receiving_bank_code = models.CharField(max_length=10, blank=True, null=True, default=None) # QR30
    channel_code = models.CharField(max_length=255, blank=True, null=True, default=None) # QR30
    # payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=255)
    # tenor = models.CharField(max_length=255, blank=True, null=True, default=None)
    # ipp_type = models.CharField(max_length=255, blank=True, null=True, default=None)
    # product_code = models.CharField(max_length=255, blank=True, null=True, default=None)
    # exchange_rate = models.CharField(max_length=255, blank=True, null=True, default=None)
    # equivalent_amount = models.CharField(max_length=255, blank=True, null=True, default=None)
    # equivalent_currency_code = models.CharField(max_length=255, blank=True, null=True, default=None)
    # company_id = models.CharField(max_length=255, blank=True, null=True, default=None)
    # invoice = models.CharField(max_length=255, blank=True, null=True, default=None)
    # note = models.TextField(blank=True)

    datetime_create = models.DateTimeField(auto_now_add=True, db_index=True)
    datetime_update = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-transaction_datetime']

    def __str__(self):
        return str(self.id)

    @staticmethod
    def complete_transaction(scb_pg_id, status_details, alert_id, is_queue = True):
        from .transaction_complete_tasks import task_complete_transaction
        if is_queue:
            task_complete_transaction.delay(scb_pg_id, status_details, alert_id)
        else:
            task_complete_transaction(**{
                'scb_pg_id': scb_pg_id,
                'status_details': status_details,
                'alert_id': alert_id
            })

'''
{
  "resCode": "00",
  "resDesc ": "success",
  "transactionId": "xxx",
  "confirmId" : "xxx"
}
'''