from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, views, status, filters
from rest_framework.response import Response
from . import models, serializers
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.

class OrderRequestViewset(viewsets.ModelViewSet):
    serializer_class = serializers.OrderRequestSerializer
    queryset = models.OrderRequest.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__email']
    search_fields = ['user__username', 'user__email']
    ordering_fields = ['created_at', 'updated_at']

    def get_permissions(self):
        if self.action in ['update', 'destroy', 'partial_update']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return models.OrderRequest.objects.all()
        else:
            return models.OrderRequest.objects.filter(user=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

class ResolveOrderViewset(viewsets.ModelViewSet):
    serializer_class = serializers.ResolvedOrderSerializer
    queryset = models.ResolvedOrder.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user__email']
    search_fields = ['tracker', 'user__email', 'user__username', 'user__userinfo__phone']
    ordering_fields = ['created_at', 'updated_at']

    def get_permissions(self):
        if self.action not in ['list']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()] 
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return models.ResolvedOrder.objects.all()
        else:
            return models.ResolvedOrder.objects.filter(user=self.request.user)
        
    def create(self, request):
        order_id=request.data.pop('order_id', None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if order_id is not None:
            order = models.OrderRequest.objects.get(id=order_id)
            user = order.user
            address = order.address
            order.delete()  
        else: user = request.user

        serializer.save(user=user, address=address) 
        
        return Response(serializer.data)
    
    def partial_update(self, request, pk=None):
        status = request.data['status']
        resolved_order = models.ResolvedOrder.objects.get(id=pk)
        
        resolved_order.update_order_status(status)

        return Response({
            "message": f'Product of tracking-id {resolved_order.tracker} status successfully updated to {status}'
        })

class TrackingOrderViewset(views.APIView):  
    def get(self, request, tracker_id):
        try:
            tracker = models.TrackingOrder.objects.get(resolved_order__tracker=tracker_id)
            serializer = serializers.TrackingOrderSerializer(tracker)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.TrackingOrder.DoesNotExist:
            return Response({'message': 'Tracker ID doesn\'t match'}, status=status.HTTP_404_NOT_FOUND)
