from rest_framework import serializers

from .models import Mailer


class MailerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailer
        fields = '__all__'
