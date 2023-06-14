from rest_framework import serializers
from .models import KYCStep1, KYCStep2, KYCStep3


class KYCStep1Serializer(serializers.ModelSerializer):
    class Meta:
        model = KYCStep1
        fields = '__all__'


class KYCStep2Serializer(serializers.ModelSerializer):
    class Meta:
        model = KYCStep2
        fields = '__all__'


class KYCStep3Serializer(serializers.ModelSerializer):
    class Meta:
        model = KYCStep3
        fields = '__all__'
