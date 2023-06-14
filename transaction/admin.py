from django.contrib import admin

from .models import Transaction, Payment


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'account',
        'transaction_hash',
        'source_key',
        'destination_key',
        'values',
        'coin',
        'method',
        'status',
        'datetime_start',
        'datetime_end',
        'datetime_complete',
        'datetime_cancel',
        'datetime_create',
        'datetime_update',
    )
    autocomplete_fields = ('account',)
    search_fields = ('id', 'transaction_hash', 'account__email', 'account__username', 'destination_key')
    list_filter = ('status', 'source_key', 'destination_key', 'transaction_hash', 'coin', 'method', 'status')
    # readonly_fields = ('account',)
    ordering = ('-datetime_update',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'code',
        'transaction',
        'ref_code_1',
        'ref_code_2',
        'transaction',
        'qrcode',
        'payment_slip',
        'datetime_create',
        'datetime_update',
        'datetime_stamp'
    )
    ordering = ('-datetime_update',)
