from rest_framework import serializers
from . import models

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
