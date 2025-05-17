from . import serializers
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User 
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate
from . import models
# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        try:
            payload = request.data
            username = payload['username']
            password = payload['password']
            email = payload['email']
            if User.objects.filter(email=email).exists():
                print('here')
                raise ValidationError("Email exists")
            phone = payload['phone']
            if models.UserModel.objects.filter(phone=phone).exists():
                raise ValidationError("Phone exists")
            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            print(user)
            models.UserModel.objects.create(user=user, phone=phone)
            return Response({'message': 'registration successful'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': str(e)
            })

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer

class UserDetailsView(APIView):
    def get(self, request, param):
        if not request.user.is_staff:
            return Response(
                {"message": "Only admin users are allowed"},
                status=status.HTTP_403_FORBIDDEN
            )
        user = get_object_or_404(User, id=param)
        return Response({
            "username": user.username,
            "email": user.email,
            "phone": user.userinfo.phone
        })
    
class AddressViews(viewsets.ModelViewSet):
    serializer_class = serializers.AddressSerializer
    permission_classes = [permissions.IsAuthenticated] 
    queryset = models.Address.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff:
            return models.Address.objects.all()
        return models.Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

#super admin things..
@api_view(['GET'])
def admins(request):
    if not request.user.is_superuser:
        return Response({"message": "Not all users are allowed"}, status=403)
    
    admins = User.objects.filter(is_staff=True).exclude(email__isnull=True).exclude(email="").values_list('email', flat=True)
    return Response({"admins": list(admins)}, status=200)

@api_view(['POST'])
def add_admin(request):
    if not request.user.is_superuser:
        return Response({"message": "Not all users are allowed"}, status=403)

    email = request.data.get('email')
    if not email:
        return Response({"message": "Email is required"}, status=400)

    try:
        user = User.objects.get(email=email)
        user.is_staff = True
        user.save()
        return Response({"message": f"{email} is now an admin."}, status=200)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=404)

@api_view(['POST'])
def remove_admin(request):
    if not request.user.is_superuser:
        return Response({"message": "Not all users are allowed"}, status=403)

    email = request.data.get('email')
    if not email:
        return Response({"message": "Email is required"}, status=400)

    try:
        user = User.objects.get(email=email)
        if user is request.user:
            return Response({"message": "you can not remove yourself as admin"}, status='403')
        
        user.is_staff = False
        user.save()
        return Response({"message": f"{email} is no longer an admin."}, status=200)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=404)