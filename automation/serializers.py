from rest_framework import serializers
from . import models

class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AutomatedOrder
        fields = '__all__'

