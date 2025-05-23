from rest_framework import serializers
from .models import MannualPayment

class MannualPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MannualPayment
        fields = '__all__'
        