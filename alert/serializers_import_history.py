import stringcase
from rest_framework import serializers

from account.serializers import AccountListMiniSerializer
from alert.models import Alert


class AlertImportHistoryEventSerializer(serializers.ModelSerializer):
    percent = serializers.SerializerMethodField()
    account = AccountListMiniSerializer()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = (
            'id',
            'status',
            'status_label',
            'account',
            'input_filename',
            'log_history_filename',
            'log_history_file_size',
            'percent',
            'module_name',
            'datetime_create'
        )

    def get_status_label(self,alert):
        return stringcase.snakecase(stringcase.lowercase(alert.status_label))

    def get_percent(self, alert):
        percent = (alert.count_row_complete*100) // alert.count_row if alert.count_row > 0 else 0
        return percent if 0 <= percent < 100 else 100


class AlertImportHistorySerializer(serializers.ModelSerializer):
    percent = serializers.SerializerMethodField()
    account = AccountListMiniSerializer()
    status_label = serializers.SerializerMethodField()
    log_history_filename = serializers.SerializerMethodField()
    is_fail = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = (
            'id',
            'status',
            'status_label',
            'account',
            'code',
            'input_filename',
            'log_history_filename',
            'log_history_file_size',
            'percent',
            'module_name',
            'action_type',
            'datetime_create',
            'datetime_end',
            'is_fail'
        )

    def get_status_label(self, alert):
        return stringcase.snakecase(alert.status_label.lower())

    def get_percent(self, alert):
        percent = (alert.count_row_complete*100) // alert.count_row if alert.count_row > 0 else 0
        return percent if 0 <= percent < 100 else 100

    def get_log_history_filename(self, alert):
        if alert.status in [3, 4]:
            return alert.log_history_filename
        else:
            return None

    def get_log_history_file_size(self, alert):
        if alert.status in [3, 4]:
            return alert.log_history_file_size
        else:
            return 0

    def get_is_fail(self, alert):
        if alert.status in [0, 1, 2]:
            return False
        if alert.status in [-5, -1] or alert.count_row_complete != alert.count_row:
            return True
        else:
            return False
