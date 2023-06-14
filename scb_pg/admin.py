from django.contrib import admin

from .models import SCBPayment


@admin.register(SCBPayment)
class LogAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'bill_payment_ref1', 'bill_payment_ref2', 'currency_code', 'transaction_type')
    search_fields = ['transaction_id', 'bill_payment_ref1', 'bill_payment_ref2', 'currency_code', 'transaction_type']
    search_fields = ('id', 'transaction_id', 'bill_payment_ref1', 'bill_payment_ref2', 'currency_code', 'transaction_type')
