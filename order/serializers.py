from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='userinfo.phone', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone']

class OrderRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = models.OrderRequest
        fields = '__all__'
        read_only_fields = ['id', 'user']
    
class ResolvedOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.ResolvedOrder
        fields = '__all__'
        read_only_fields = ['id', 'user']

class TrackingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model =  models.TrackingOrder
        fields = '__all__'
        read_only_fields = ['is_paid', 'is_shipped', 'is_received']