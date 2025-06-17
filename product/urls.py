from django.urls import path,include
from . import views
from . import bkash_views

from rest_framework.routers import SimpleRouter
router = SimpleRouter(trailing_slash='')

router.register(r'category', views.CategoryView, basename='category')
router.register(r'order', views.ProductView, basename='product')  

urlpatterns = [
    path('', include(router.urls)),
    path('place-order', views.OrderView.as_view(), name='order'),
    path('place-order/<uuid:tracker>', views.OrderView.as_view(), name='order-detail'),
    path('bkash/callback', bkash_views.bkash_callback, name='bkash-url'),
]
