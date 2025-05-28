from django.shortcuts import render
from .models import Blog
from .serializers import BlogSerializer
# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
import cloudinary
import logging

logger = logging.getLogger(__name__)

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

class BlogView(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes=[IsAdminUser]
    serializer_class = BlogSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return []
    
    def create(self, request, *args, **kwargs):
        try:
            image_file = request.FILES.get('image')

            if image_file:
                # Validate image
                is_valid, error_message = validate_image(image_file)
                if not is_valid:
                    return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    image_file,
                    folder="blog",
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
            logger.error(f"Error creating blog: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def perform_destroy(self, request, *args, **kwargs):
        try:
            # Retrieve the instance to be deleted
            instance = self.get_object()

            # Check if the instance has an image associated with it
            if instance.image:
                try:
                    # Get the public_id from the Cloudinary image URL
                    public_id = instance.public_id
                    # Delete the image from Cloudinary
                    cloudinary.uploader.destroy(public_id)
                except Exception as e:
                    logger.warning(f"Failed to delete old image from Cloudinary: {str(e)}")

            # Call the parent class's perform_destroy method to actually delete the instance
            super().perform_destroy(request, *args, **kwargs)

        except Exception as e:
            logger.error(f"Error deleting blog: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)