from rest_framework import serializers
from . import models
class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderRequest
        fields = ['id', 'product_url', 'quantity', 'description', 'status']
    
class ResolvedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResolvedOrder
        fields = '__all__'
        read_only_fields = ['tracker']

class TrackingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model =  models.TrackingOrder
        fields = '__all__'