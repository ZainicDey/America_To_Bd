from django.contrib.auth.models import User
from rest_framework import serializers
from . import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Ensure the user is active
        if not self.user.is_active:
            raise serializers.ValidationError("User account is inactive.")
        
        # Add custom claims to the response data
        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser
        return data

# class AddressSerializer(serializers.ModelSerializer):
#      class Meta:
#         model =  models.Address
#         fields = '__all__'