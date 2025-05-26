from rest_framework import serializers
from .models import MannualPayment

class MannualPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MannualPayment
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'image': {'required': False},
            'public_id': {'required': False}
        }