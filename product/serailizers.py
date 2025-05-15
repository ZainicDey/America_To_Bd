from rest_framework import serializers
from . import models

class ColorSeriailizer(serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = '__all__'

class CategorySeriailizer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'

class ProductSerializers(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Category.objects.all()
    )
    color = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=models.Color.objects.all()
    )
    class Meta:
        model = models.Product
        fields = '__all__' 