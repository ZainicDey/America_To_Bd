from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'category', views.CategoryView, basename='category')
router.register(r'', views.ProductView, basename='product')  

urlpatterns = [
    path('', include(router.urls)),
]
