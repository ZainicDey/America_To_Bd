from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'', views.ProductView, basename='product')
router.register(r'category', views.CategoryView, basename='prodcategory')
router.register(r'color', views.ColorView, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('category/', views.CategoryView.as_view)
]
