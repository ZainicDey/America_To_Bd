from django.urls import path, include
from . import views

from rest_framework.routers import SimpleRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CustomTokenObtainPairView
from rest_framework.routers import DefaultRouter

router = SimpleRouter(trailing_slash='')

router.register(r'address', views.AddressViews)

urlpatterns = [
    path('auth/signup', views.RegisterView.as_view(), name='register'),
    path('auth/signin', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('auth/refresh', TokenRefreshView.as_view(), name='refresh'),

    path('user', views.UserDetailsView.as_view()),
    path('user/<int:param>', views.UserDetailsView.as_view()),
    path('', include(router.urls)),
    path('profile', views.ProfileViewUpdate.as_view(), name='profile'),

    path('superadmin/get_admin', views.admins),
    path('superadmin/add_admin', views.add_admin),
    path('superadmin/remove_admin', views.remove_admin),

    #otp
    path("auth/send-otp", views.SendOTPView.as_view()),
    path("auth/verify-otp", views.VerifyOTPView.as_view()),
]
