from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CustomTokenObtainPairView

urlpatterns = [
    path('auth/signup/', views.RegisterView.as_view(), name='register'),
    path('auth/signin/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('user/<int:param>', views.UserDetailsView.as_view()),
]
