from django.shortcuts import render
from rest_framework import viewsets, permissions, views, status
from rest_framework.response import Response
from . import models, serializers
# Create your views here.

class OrderRequestViewset(viewsets.ModelViewSet):
    serializer_class = serializers.OrderRequestSerializer
    queryset = models.OrderRequest.objects.all()

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

    def get_permissions(self):
        if self.action not in ['list']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()] 
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return models.ResolvedOrder.objects.all()
        else:
            return models.ResolvedOrder.objects.filter(order__user=self.request.user)

class TrackingOrderViewset(views.APIView):  
    def get(self, request, tracker_id):
        try:
            tracker = models.TrackingOrder.objects.get(resolved_order__tracker=tracker_id)
            serializer = serializers.TrackingOrderSerializer(tracker)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.TrackingOrder.DoesNotExist:
            return Response({'message': 'Tracker ID doesn\'t match'}, status=status.HTTP_404_NOT_FOUND)
