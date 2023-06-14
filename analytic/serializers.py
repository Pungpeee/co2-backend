from rest_framework import serializers

from .models import Session, SessionLog, VisitorLog


class SessionSerializer(serializers.ModelSerializer):
    source_display = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ('account',
                  'source',
                  'source_display',
                  'ip',
                  'datetime_create'
                  )

    def get_source_display(self, instance):
        return instance.get_source_display()


class SessionLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = SessionLog
        fields = ('count', 'date', 'datetime_create')


class VisitorLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisitorLog
        fields = ('count', 'date', 'datetime_create')
