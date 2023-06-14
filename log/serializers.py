from rest_framework import serializers, status

from .models import Log


class MiniLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = (
            'id', 'payload'
        )


class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = (
            'id', 'group', 'code', 'status', 'status_code', 'payload', 'datetime_create'
        )