from rest_framework import serializers

from alert.models import Alert


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ('id', 'status', 'status_label', 'count_row', 'count_row_complete', 'datetime_update')
