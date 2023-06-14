from django.contrib import admin

from account.caches import cache_account_delete
from account.models import Account, Forgot, RequestDelete, IdentityVerification, KYCAccount, UtilityToken, KYCStep1, \
    KYCStep2, KYCStep3


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'external_id',
        'code',
        'username',
        'email',
        'first_name',
        'last_name',
        'datetime_update',
        'type',
        'is_force_reset_password',
        'is_active',
        'is_accepted_active_consent',
    )
    readonly_fields = ('user_permissions',)
    actions = ['set_type_to_system_user', 'clear_cached']
    search_fields = ['external_id', 'code', 'username', 'email', 'first_name', 'last_name']

    @staticmethod
    def set_type_to_system_user(self, request, queryset):
        queryset.update(type=1)

    @staticmethod
    def set_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @staticmethod
    def clear_cached(self, request, queryset):
        for account in queryset:
            cache_account_delete(account.id)


@admin.register(Forgot)
class ForgetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'account',
        'token',
        'status',
        'method',
        'datetime_create',
        'send_method',
        'count_failed',
        'datetime_failed_limit'
    )


@admin.register(RequestDelete)
class ForgetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'account',
        'token',
        'datetime_create'
    )


@admin.register(IdentityVerification)
class IdentityVerificationAdmin(admin.ModelAdmin):
    list_display = (
        'token',
        'account',
        'status',
        'method',
        'send_method',
        'datetime_create',
        'datetime_expire',
    )
    search_fields = ('account__username', 'account__email', 'account__first_name', 'token')


@admin.register(KYCAccount)
class KYCAccountAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'account',
        'first_name',
        'last_name',
        'is_accepted_kyc_consent',
        'kyc_status',
        'phone',
        'date_birth',
        'datetime_create',
        'is_mobile_verify'
    )
    search_fields = ['first_name', 'last_name']
    list_filter = ['kyc_status']


@admin.register(UtilityToken)
class UtilityTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'account', 'is_active', 'datetime_expire', 'datetime_create']
    search_fields = ['id', 'account']
    list_filter = ['name']


@admin.register(KYCStep1)
class KYCStep1Admin(admin.ModelAdmin):
    list_display = ['id', 'status', 'account']
    list_filter = ['status']
    search_fields = ['id']


@admin.register(KYCStep2)
class KYCStep2Admin(admin.ModelAdmin):
    list_display = ['id', 'status', 'account']
    list_filter = ['status']
    search_fields = ['id']


@admin.register(KYCStep3)
class KYCStep3Admin(admin.ModelAdmin):
    list_display = ['id', 'status', 'account']
    list_filter = ['status']
    search_fields = ['id']
