from rest_framework import viewsets, permissions
from . import models, serailizers
# Create your views here.

class ProductView(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serailizers.ProductSerializers

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
class CategoryView(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serailizers.CategorySeriailizer
    permission_classes = [permissions.IsAdminUser]

class ColorView(viewsets.ModelViewSet):
    queryset = models.Color.objects.all()
    serializer_class = serailizers.ColorSeriailizer
    permission_classes = [permissions.IsAdminUser]