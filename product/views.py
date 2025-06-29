from . import models, serializers
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import cloudinary
import cloudinary.uploader
from django.conf import settings
import logging

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from .filters import ProductFilter
from resend import Emails
logger = logging.getLogger(__name__)

from .bkash_views import bkash_url

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

def validate_image(image_file):
    """Validate image file before upload"""
    if not image_file:
        return False, "No image file provided"
    
    # Check file size (max 5MB)
    if image_file.size > 5 * 1024 * 1024:
        return False, "Image size should not exceed 5MB"
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if image_file.content_type not in allowed_types:
        return False, "Only JPEG, PNG and GIF images are allowed"
    
    return True, None
import json
class ProductView(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializers
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter  # Use the custom filter class here
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'price']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        try:
            image_files = request.FILES.getlist('image') 
            image_urls = []
            public_ids = []

            for image_file in image_files:
                is_valid, error_message = validate_image(image_file)
                if not is_valid:
                    return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

                upload_result = cloudinary.uploader.upload(
                    image_file,
                    folder="products",
                    resource_type="image"
                )
                image_urls.append(upload_result.get('secure_url'))
                public_ids.append(upload_result.get('public_id'))

            data = request.data.copy()
            data['image'] = json.dumps(image_urls)
            data['public_id'] = json.dumps(public_ids)
            print(data)
            serializer = self.get_serializer(data=data)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        try:
            image_files = self.request.FILES.getlist('image')  # Multiple images
            instance = self.get_object()

            if image_files:
                # Delete old images
                if instance.public_id:
                    for pid in instance.public_id:
                        try:
                            cloudinary.uploader.destroy(pid)
                        except Exception as e:
                            logger.warning(f"Failed to delete image with public_id '{pid}': {str(e)}")

                image_urls = []
                public_ids = []

                # Validate and upload new images
                for image_file in image_files:
                    is_valid, error_message = validate_image(image_file)
                    if not is_valid:
                        raise ValueError(error_message)

                    upload_result = cloudinary.uploader.upload(
                        image_file,
                        folder="products",
                        resource_type="image"
                    )

                    image_urls.append(upload_result.get('secure_url'))
                    public_ids.append(upload_result.get('public_id'))  # Save full public_id now

                # Save updated image URLs and public IDs
                print(image_urls)
                serializer.save(image=image_urls, public_id=public_ids)
            else:
                serializer.save()
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise

    
class CategoryView(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAdminUser]

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
        
    def get(self, request, tracker=None):

        if tracker:
            try:
                order = Order.objects.get(tracker=tracker)
            except Order.DoesNotExist:
                return Response({'detail': 'Order not found.'}, status=404)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
            
        queryset = self.get_queryset()
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data, status=200)
        
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)

            if order.transactionId is None:
                # Initiate bKash payment and get URL
                payment_url = bkash_url(order.tracker)
                if payment_url:
                    return Response({"url": payment_url}, status=status.HTTP_201_CREATED)
                return Response({"error": "Failed to initiate bKash payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, tracker):
        if not request.user.is_staff:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.get(tracker=tracker)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        Emails.send({
            "from": "America to BD <noreply@americatobd.com>",
            "to": [order.user.email],
            "subject": "Payment was invalid - America to BD",
            "html": f"""
            <h2>Your payment is cancelled</h2>
            <p>Dear {order.user.first_name} {order.user.last_name},</p>
            <p>We have checked your payment and unfortunately, it was invalid. Please contact our support team for more details.</p>
            """
        })
        return Response({'detail': 'Order deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, tracker):
        if not request.user.is_staff:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.get(tracker=tracker)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        status_value = request.data.get('status')
        if status_value:
            order.status = status_value
            order.save()
            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [order.user.email],
                "subject": f"Order status for {tracker} - America to BD",
                "html": f"""
                <h2>Your order status is now: {status_value}</h2>
                <p>Dear {order.user.first_name} {order.user.last_name},</p>
                <p>We've updated your order status. Please contact support if you have questions.</p>
                """
            })
            return Response({'detail': 'Order status updated successfully.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
