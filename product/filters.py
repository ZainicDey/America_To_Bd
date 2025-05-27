from django_filters import rest_framework as filters
from django.db.models import JSONField
from django_filters.filters import CharFilter
from .models import Product

class ProductFilter(filters.FilterSet):
    # Custom filters for JSON fields using 'contains' lookup
    color = CharFilter(field_name='color', lookup_expr='contains')
    size = CharFilter(field_name='size', lookup_expr='contains')

    class Meta:
        model = Product
        fields = ['category', 'color', 'size']