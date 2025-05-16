from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'', views.ProductView, basename='product')
router.register(r'category', views.CategoryView, basename='prodcategory')

urlpatterns = [
    path('', include(router.urls)),
]
