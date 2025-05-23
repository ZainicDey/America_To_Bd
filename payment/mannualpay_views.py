from rest_framework.viewsets import ModelViewSet
from .models import MannualPayment
from .serializers import MannualPaymentSerializer
from rest_framework.permissions import IsAdminUser,IsAuthenticated

class MannualPaymentView(ModelViewSet):
    queryset = MannualPayment.objects.all()
    serializer_class = MannualPaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MannualPayment.objects.filter(user=self.request.user)
