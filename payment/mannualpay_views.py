from rest_framework.viewsets import ModelViewSet
from rest_framework import views
from .models import MannualPayment
from .serializers import MannualPaymentSerializer
from rest_framework.permissions import IsAuthenticated
from order.models import ResolvedOrder
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
import cloudinary
import cloudinary.uploader
from django.conf import settings
import logging
from resend import Emails


logger = logging.getLogger(__name__)

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

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS) for all
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions require owner or admin
        return obj.user == request.user or request.user.is_staff

class MannualPaymentView(ModelViewSet):
    serializer_class = MannualPaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'tracker'

    def get_queryset(self):
        """Return payments for current user, or all for admin"""
        queryset = MannualPayment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Add tracker filtering if provided in query params
        tracker = self.request.query_params.get('tracker')
        if tracker:
            queryset = queryset.filter(tracker=tracker)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            image_file = request.FILES.get('image')
            tracker = request.data.get('tracker')

            # Check for existing resolved order
            if MannualPayment.objects.filter(tracker=tracker).exists():
                return Response(
                    {'tracker': 'This order already has a payment. Delete existing payment to reprocess.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if image_file:
                # Validate image
                is_valid, error_message = validate_image(image_file)
                if not is_valid:
                    return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    image_file,
                    folder="mannual_payments",
                    resource_type="image"
                )
                image_url = upload_result.get('secure_url')
                public_id = upload_result.get('public_id')
                data = request.data.copy()
                data['image'] = image_url
                data['public_id'] = public_id
                serializer = self.get_serializer(data=data)
            else:
                serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating manual payment: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def list(self, request, *args, **kwargs):
    #     """Custom list to handle empty results gracefully"""
    #     queryset = self.filter_queryset(self.get_queryset())
        
    #     if not queryset.exists() and request.query_params.get('tracker'):
    #         return Response(
    #             {'detail': 'No manual payment found for this tracker'},
    #             status=status.HTTP_404_NOT_FOUND
    #         )
            
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

class ApprovePaymentView(views.APIView):
    def post(self, request):
        if not request.user.is_staff:
            return Response({"message": "You are not authorized to approve payments"}, status=status.HTTP_403_FORBIDDEN)
        
        tracker_id = request.data.get('tracker_id')
        resolved_order = ResolvedOrder.objects.get(tracker=tracker_id)
        email = resolved_order.user.email

        resolved_order.update_order_status('PD')
        
        mannual_payment = MannualPayment.objects.get(tracker=tracker_id)
        mannual_payment.delete()

        Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [email],
                "subject": "Payment Confirmation - America to BD",
                "html": f"""
                <h2>We have aproved your payment!</h2>
                <p>Dear {resolved_order.user.first_name} {resolved_order.user.last_name},</p>
                <p>Thanks for using our service. We have approved your payment. Your order is being processed.</p>
                <p>You can track your order status using your tracking ID.</p>
                <p>Tracking ID: {tracker_id}<p>
                <p>Thank you for choosing America to BD!</p>
                """
            })

        return Response({"message": "Payment approved successfully"}, status=status.HTTP_200_OK)
