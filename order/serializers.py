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
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), write_only=True, source='address', required=False, allow_null=True
    )

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
        read_only_fields = ['is_paid', 'is_shipped', 'is_received']