from rest_framework import viewsets, permissions, views, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from . import models, serializers
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound
from resend import Emails
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Only allow delete if user is owner or admin
        if request.method == 'DELETE':
            return obj.user == request.user or request.user.is_staff
        return True

class OrderRequestViewset(viewsets.ModelViewSet):
    serializer_class = serializers.OrderRequestSerializer
    queryset = models.OrderRequest.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__email']
    search_fields = ['user__username', 'user__email']
    ordering_fields = ['created_at', 'updated_at']

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAdminUser()]
        elif self.action == 'destroy':
            return [IsOwnerOrAdmin()]
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
    
# class ResolvedOrderPagination(PageNumberPagination):
    """"
    {
        "count": 123,
        "next": "http://america-to-bd.vercel.app/order/resolved_order/?page=2",
        "previous": null,
        "results": [
            {...}, {...}, ...
        ]
    }
    """
#     page_size = 5  # Customize the number of items per page
#     page_size_query_param = 'page_size'
#     max_page_size = 100

class ResolveOrderViewset(viewsets.ModelViewSet):
    serializer_class = serializers.ResolvedOrderSerializer
    queryset = models.ResolvedOrder.objects.all()
    # pagination_class = ResolvedOrderPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user__email']
    search_fields = ['tracker', 'user__email', 'user__username', 'user__userinfo__phone']
    ordering_fields = ['created_at', 'updated_at']

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAdminUser()]
        elif self.action == 'destroy':
            return [IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return models.ResolvedOrder.objects.all()
        else:
            return models.ResolvedOrder.objects.filter(user=self.request.user)
        

    def create(self, request):
        order_id = request.data.pop('order_id', None)
        email = request.data.pop('email', None)
        address = None
        print(order_id)

        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise NotFound("User with this email does not exist.")
        elif order_id:
            try:
                order = models.OrderRequest.objects.get(id=order_id)
                user = order.user
                address = order.address
                order.delete()
            except models.OrderRequest.DoesNotExist:
                raise NotFound("OrderRequest with this ID does not exist.")
        else:
            user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resolved_order = serializer.save(user=user, address=address)

        # Send confirmation email using Resend
        try:
            if not settings.RESEND_API_KEY:
                logger.error("RESEND_API_KEY is not set in settings")
                raise ValueError("RESEND_API_KEY is not configured")
            
            # Temporary debug code
            print(f"API Key length: {len(settings.RESEND_API_KEY) if settings.RESEND_API_KEY else 0}")
            print(f"API Key starts with: {settings.RESEND_API_KEY[:10] if settings.RESEND_API_KEY else 'None'}")

            logger.info(f"Attempting to send email to {user.email}")
            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [user.email],
                "subject": "Order Confirmation - America to BD",
                "html": f"""
                <h2>Your order has been confirmed!</h2>
                <p>Dear {user.username},</p>
                <p>Your order has been successfully created with the following details:</p>
                <ul>
                    <li>Tracking ID: {resolved_order.tracker}</li>
                    <li>Product URL: {resolved_order.product_url}</li>
                    <li>Quantity: {resolved_order.quantity}</li>
                    <li>Total Cost: ${resolved_order.cost}</li>
                </ul>
                <p>You can track your order status using your tracking ID.</p>
                <p>Thank you for choosing America to BD!</p>
                """
            })
            logger.info(f"Successfully sent email to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {str(e)}", exc_info=True)
            print(f"Failed to send confirmation email: {str(e)}")

        return Response(serializer.data)

    
    def partial_update(self, request, pk=None):
        status = request.data['status']
        resolved_order = get_object_or_404(models.ResolvedOrder, id=pk)
        
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
