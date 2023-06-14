from django.contrib import admin

# Register your models here.
from activity.models import CarbonActivity


@admin.register(CarbonActivity)
class CarbonActivityAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(CarbonActivityAdmin, self).get_queryset(request)
        return qs.exclude(transaction__account=None)

    list_display = (
        'id', 'transaction_id', 'get_account',
        'type', 'activity_code', 'activity_name', 'activity_details',
        'carbon_saving', 'desc','datetime_update'
    )
    autocomplete_fields = ('transaction',)
    search_fields = (
        'id', 'transaction_id', 'transaction__account__email',
        'type', 'activity_code', 'activity_name', 'activity_details',
        'carbon_saving', 'desc','datetime_update'
    )

    readonly_fields = ('transaction',)
    ordering = ('-datetime_update',)
