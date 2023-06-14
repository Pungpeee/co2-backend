from rest_framework import serializers

from config.models import Config


class ConfigSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = Config 
        fields = (
            'app',
            'type',
            'type_display',
            'value',
        )

    def get_type_display(self, config):
        return config.get_type_display()

    def get_value(self, config):
        return config.get_value()


class ConfigUpdateSerializer(serializers.Serializer):
    value = serializers.CharField(required=True)


class ImportConfigSerializer(serializers.Serializer):
    file = serializers.FileField()
