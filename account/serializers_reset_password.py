import re

from django.http import Http404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from account.caches import cache_account_delete
from account.models import PasswordHistory
from account.models import Forgot, Account, PasswordHistory
from config.models import Config
from log.models import Log


class ResetPasswordSerializer(serializers.Serializer):
    method = serializers.IntegerField(default=0)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def create(self, validated_data):
        _forgot = Forgot.objects.filter(
            token=validated_data['token'],
            method=validated_data['method'],
            status=1
        ).first()

        if _forgot is None:
            raise Http404

        account = Account.objects.get(id=_forgot.account_id)
        account.set_password(validated_data['new_password'])
        account.is_force_reset_password = False
        account.save(update_fields=['password', 'is_force_reset_password', 'datetime_update'])
        Log.push(None, 'ACCOUNT', 'RESET_PASSWORD', account, 'User is update password', status.HTTP_200_OK)
        PasswordHistory.objects.create(account=account, password=account.password)
        Forgot.objects.filter(account_id=account.id, status=1).update(status=-1)
        _forgot.status = 2
        _forgot.save(update_fields=['status'])
        cache_account_delete(account.id)

        return account

    def validate(self, attrs):
        message_error = list()
        config_value = Config.pull_value('config-account-condition-password')
        if config_value:
            for key_condition in config_value:
                _ = config_value[key_condition]
                if _['is_use']:
                    if re.compile(_['compile']).search(attrs['new_password']) is None:
                        message_error.append(_['name'])

        forgot = Forgot.objects.filter(
            token=attrs['token'],
            method=attrs['method'],
            status=1
        ).first()
        if forgot:
            check_password = PasswordHistory.check_exists(forgot.account, attrs['new_password'])
            if not check_password:
                message_error.append('error_password_must_differ')
        if attrs['new_password'] != attrs['confirm_password']:
            message_error.append('password_not_match')
        if message_error.__len__() > 0:
            raise ValidationError({'new_password': message_error})
        return attrs
