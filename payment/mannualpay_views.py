from rest_framework.viewsets import ModelViewSet
from .models import MannualPayment
from .serializers import MannualPaymentSerializer

class MannualPaymentView(ModelViewSet):
    queryset = MannualPayment.objects.all()
    serializer_class = MannualPaymentSerializer
    
