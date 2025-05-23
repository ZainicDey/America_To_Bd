from . import models, serializers
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import cloudinary
import cloudinary.uploader
from django.conf import settings
import logging

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

class ProductView(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializers
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'price']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def create(self, request, *args, **kwargs):
        try:
            image_file = request.FILES.get('image')

            print(image_file)
            
            if image_file:
                # Validate image
                is_valid, error_message = validate_image(image_file)
                if not is_valid:
                    return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    image_file,
                    folder="products",
                    resource_type="image"
                )
                image_url = upload_result.get('secure_url')
                print(image_url)
                data = request.data.copy()
                data['image'] = image_url
                serializer = self.get_serializer(data=data)
            else:
                serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        try:
            image_file = self.request.FILES.get('image')
            instance = self.get_object()

            if image_file:
                # Validate image
                is_valid, error_message = validate_image(image_file)
                if not is_valid:
                    raise ValueError(error_message)

                # Delete old image if exists
                if instance.image:
                    try:
                        public_id = instance.image.split('/')[-1].split('.')[0]
                        cloudinary.uploader.destroy(public_id)
                    except Exception as e:
                        logger.warning(f"Failed to delete old image: {str(e)}")

                # Upload new image
                upload_result = cloudinary.uploader.upload(
                    image_file,
                    folder="products",
                    resource_type="image"
                )
                image_url = upload_result.get('secure_url')
                serializer.save(image=image_url)
            else:
                serializer.save()
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise
    
class CategoryView(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAdminUser]