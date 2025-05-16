from rest_framework import serializers
from . import models

class CategorySeriailizer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class ProductSerializers(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Category.objects.all()
    )
    class Meta:
        model = models.Product
        fields = '__all__' 