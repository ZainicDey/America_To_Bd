from rest_framework import serializers
from . import models
from userrole.serializers import UserSerializer, AddressSerializer
class AutomationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    class Meta:
        model = models.AutomatedOrder
        fields = '__all__'
        read_only_fields = ['id', 'user', 'address']

