
from rest_framework import serializers

from .models import Term, Consent


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['id', 'topic', 'body', 'is_publish', 'created_by', 'datetime_create']


class ConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consent
        fields = ['id', 'account_id', 'term_id', 'datetime_create']