from rest_framework import serializers
from . import models
from .models import Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'
    

class ProductSerializers(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Category.objects.all()
    )
    image = serializers.URLField(required=False, allow_null=True)
    
    class Meta:
        model = models.Product
        fields = '__all__'

    def to_internal_value(self, data):
        # Convert 'category' to lowercase before field-level processing
        data = data.copy()  # avoid mutating original input
        if 'category' in data and isinstance(data['category'], str):
            data['category'] = data['category'].lower()
        return super().to_internal_value(data)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'color', 'size', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'tracker', 'user', 'address', 'product', 'totalPrice', 'status',
            'contactNo', 'email', 'transactionId', 'payMethod',
            'shippingMethod', 'shippingCost', 'items'
        ]
    
    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name
        }

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        OrderItem.objects.bulk_create([
            OrderItem(order=order, **item) for item in items_data
        ])
        return order