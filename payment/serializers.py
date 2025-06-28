from rest_framework import serializers
from .models import MannualPayment
from order.models import ResolvedOrder
class MannualPaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    class Meta:
        model = MannualPayment
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'image': {'required': False},
            'public_id': {'required': False}
        }
        read_only_fields = ('created_at', 'updated_at,  order_id')

    def get_order_id(self, obj):
        order = ResolvedOrder.objects.filter(tracker=obj.tracker).first()
        if order:    
            return order.id
        else :
            return None