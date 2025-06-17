from rest_framework import serializers
from . import models
from django.contrib.auth.models import User
from userrole.models import Address

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='userinfo.phone', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class OrderRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), write_only=True, required=True
    )
    address_details = AddressSerializer(source='address', read_only=True)

    class Meta:
        model = models.OrderRequest
        fields = '__all__'
        read_only_fields = ['id', 'user']
    
class ResolvedOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = models.ResolvedOrder
        fields = '__all__'
        read_only_fields = ['id', 'user', 'address']

class TrackingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model =  models.TrackingOrder
        fields = '__all__'
        read_only_fields = ['is_paid', 'is_shipped_in_usa', 'is_received', 'is_canceled', 'is_on_board', 'is_landed_in_bd', 'is_ready_to_delivery']