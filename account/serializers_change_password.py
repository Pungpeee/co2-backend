import re

from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, NotAuthenticated, ValidationError

from account.models import Account, PasswordHistory
from config.models import Config
from log.models import Log
from utils.generator import generate_token


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                account = Account.objects.get(id=request.user.id)
            except Account.DoesNotExist:
                raise NotFound
            else:
                _new_password = validated_data.get('new_password')
                account.set_password(_new_password)
                account.save(update_fields=['password'])
                Log.push(request, 'ACCOUNT', 'RESET_PASSWORD', account, 'User is update password', status.HTTP_200_OK)
                PasswordHistory.objects.create(account=account, password=account.password)
                token = generate_token(32)
                account.forgot_set.create(status=2, method=3, token=token)
                Account.send_change_password_noti(account.email)
                return account
        else:
            raise NotAuthenticated

    def validate_old_password(self, value):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        if user:
            if not user.check_password(value):
                raise serializers.ValidationError('Invalid Old password')
        return value

    def validate_new_password(self, value):
        message_error = list()
        config_value = Config.pull_value('config-account-condition-password')
        if config_value:
            for key_condition in config_value:
                _ = config_value[key_condition]
                if _['is_use']:
                    if re.compile(_['compile']).search(value) is None:
                        message_error.append(_['name'])

        request = self.context.get('request')
        check_password = PasswordHistory.check_exists(request.user, value)
        if not check_password:
            message_error.append('error_password_must_differ')

        if message_error.__len__() > 0:
            raise ValidationError(message_error)
        return value
