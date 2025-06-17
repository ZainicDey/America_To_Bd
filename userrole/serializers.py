from django.contrib.auth.models import User
from rest_framework import serializers
from . import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from userrole.models import UserModel

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field (inherited)
        self.fields.pop('username')

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        password = attrs.get('password')

        if not (email or phone):
            raise serializers.ValidationError('Must provide either email or phone')

        try:
            if email:
                user = User.objects.get(email=email)
            else:
                user_model = UserModel.objects.get(phone=phone)
                user = user_model.user

        except (User.DoesNotExist, UserModel.DoesNotExist):
            raise serializers.ValidationError('No active account found with the given credentials')

        if not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')

        if not user.is_active:
            raise serializers.ValidationError('User account is inactive')

        # This is critical: pass actual user for token generation
        data = super().get_token(user)
        return {
            'refresh': str(data),
            'access': str(data.access_token),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        }

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True}
        }

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='userinfo.phone')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']
