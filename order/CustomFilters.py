# filters.py
import django_filters
from .models import ResolvedOrder

class ResolvedOrderFilter(django_filters.FilterSet):
    status_not = django_filters.CharFilter(field_name='status', exclude=True)

    class Meta:
        model = ResolvedOrder
        fields = ['status', 'status_not', 'user__email']