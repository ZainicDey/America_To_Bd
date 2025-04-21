from . import serializers
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User 
from datetime import datetime
from django.shortcuts import get_object_or_404
import jwt
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView
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
            "username": user.name,
            "email": user.email,
            "phone": user.userinfo.phone
        })