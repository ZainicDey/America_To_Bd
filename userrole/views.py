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
from django.db.models import Q
from resend import Emails
from order.serializers import UserSerializer
# Create your views here.
import requests
from django.core.cache import cache
import random
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

# --- OTP Sending Logic ---
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_smsnoc(phone, otp):
    url = "https://app.smsnoc.com/api/v3/sms/send"
    headers = {
        "Authorization": f"Bearer {settings.OTP_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "recipient": phone,
        "sender_id": "8809617611313",  # must be approved
        "type": "plain",
        "message": f"Your OTP is {otp}. It will expire in 5 minutes."
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.json()

# --- OTP Send View ---
class SendOTPView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"error": "Phone is required"}, status=400)
        
        if not models.UserModel.objects.filter(phone=phone).exists(): 
            return Response({"error": "Phone number not registered"}, status=400)  
        
        otp = generate_otp()
        cache.set(f"otp:{phone}", otp, timeout=300)

        status_code, response_data = send_otp_via_smsnoc(phone, otp)
        if status_code != 200:
            return Response({"error": "Failed to send OTP", "details": response_data}, status=500)

        return Response({"message": f"OTP sent to {phone}."})

# --- OTP Verify View ---
class VerifyOTPView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        otp = request.data.get("otp")

        if not phone or not otp:
            return Response({"error": "Phone and OTP are required"}, status=400)

        cached_otp = cache.get(f"otp:{phone}")
        if cached_otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        user_model = models.UserModel.objects.filter(phone=phone).first()

        if not user_model:
            user = User.objects.create(username=phone)
            user_model = models.UserModel.objects.create(user=user, phone=phone)
        else:
            user = user_model.user

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser
        })

class RegisterView(APIView):
    def post(self, request):
        try:
            payload = request.data
            first_name = payload['first_name'] or None
            last_name = payload['last_name'] or None
            password = payload['password']
            email = payload['email'] or None
            phone = payload['phone']

            if not email or not first_name or not last_name or not password or not phone:
                raise ValidationError("All fields are required")
            
            if len(phone) > 20:
                raise ValidationError("Phone number must be 11 digits")
            
            if User.objects.filter(email=email).exists():
                print('here')
                raise ValidationError("Email exists")
            phone = payload['phone']
            if models.UserModel.objects.filter(phone=phone).exists():
                raise ValidationError("Phone exists")
            user = User.objects.create(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            user.set_password(password)
            user.save()
            print(user)
            models.UserModel.objects.create(user=user, phone=phone)

            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [email],
                "subject": "Thanks for signing up to America to BD",
                "html": f"""
                <h2>Sign up Email: {email} | Phone: {phone}</h2>
                <p>To login into our website, please use the following link: <a href="https://americatobd.com/auth/signin">Login</a></p>
                """
            })

            return Response({'message': 'registration successful'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'code': status.HTTP_400_BAD_REQUEST,
                'message': str(e)
            })


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer

class UserDetailsView(APIView):
    def get(self, request, param=None):
        if not request.user.is_staff:
            return Response({"message": "Only admin users are allowed"}, status=status.HTTP_403_FORBIDDEN)

        if not param:
            users = User.objects.all()

            # Filtering logic
            username = request.query_params.get("username")
            email = request.query_params.get("email")
            phone = request.query_params.get("phone")

            if username:
                users = users.filter(
                    Q(first_name__icontains=username) | Q(last_name__icontains=username)
                )
            if email:
                users = users.filter(email__icontains=email)
            if phone:
                users = users.filter(userinfo__phone__icontains=phone)

            return Response(UserSerializer(users, many=True).data)

        user = get_object_or_404(User, id=param)
        return Response({
            "username": user.username,
            "email": user.email,
            "phone": user.userinfo.phone
        })

    
class ProfileViewUpdate(APIView):
    serializers_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = self.serializers_class(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        phone = request.data.pop("phone", None)
        
        # Update user first
        serializer = self.serializers_class(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Now handle phone update
            if phone:
                user_model = request.user.userinfo
                user_model.phone = phone
                user_model.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        phone = request.data.pop("phone", None)
        
        # Update user first
        serializer = self.serializers_class(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Now handle phone update
            if phone:
                user_model = request.user.userinfo
                user_model.phone = phone
                user_model.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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