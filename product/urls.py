from django.urls import path,include
from . import views

from rest_framework.routers import SimpleRouter
router = SimpleRouter(trailing_slash='')

router.register(r'category', views.CategoryView, basename='category')
router.register(r'order', views.ProductView, basename='product')  

urlpatterns = [
    path('', include(router.urls)),
]
