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

    def list(self, request):
        if request.user.is_staff:
            orders = models.OrderRequest.objects.all()
        else:
            orders = models.OrderRequest.objects.filter(user=request.user)

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

class ResolveOrderViewset(viewsets.ModelViewSet):
    serializer_class = serializers.ResolvedOrderSerializer
    queryset = models.ResolvedOrder.objects.all()

    def get_permissions(self):
        return [permissions.IsAdminUser()]
    

class TrackingOrderViewset(views.APIView):  
    def get(self, request):
        tracker_id = request.GET.get('tracker_id')

        if not tracker_id:
            return Response({'message': 'Tracker ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tracker = models.TrackingOrder.objects.get(ResolvedOrder__tracker=tracker_id)
            serializer = serializers.TrackingOrderSerializer(tracker)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.TrackingOrder.DoesNotExist:
            return Response({'message': 'Tracker ID doesn\'t match'}, status=status.HTTP_401)      
    