from django_filters import rest_framework as filters
from .models import ResolvedOrder

class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class ResolvedOrderFilter(filters.FilterSet):
    status_not = CharInFilter(field_name='status', exclude=True)

    class Meta:
        model = ResolvedOrder
        fields = ['status', 'status_not', 'user__email']
