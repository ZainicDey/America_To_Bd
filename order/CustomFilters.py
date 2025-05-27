import django_filters
from django_filters.filters import BaseInFilter
from .models import ResolvedOrder
class CharInFilter(BaseInFilter, django_filters.CharFilter):
    pass

class ResolvedOrderFilter(django_filters.FilterSet):
    status_not = CharInFilter(field_name='status', exclude=True)

    class Meta:
        model = ResolvedOrder
        fields = ['status', 'status_not', 'user__email']