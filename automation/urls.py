from . import views, bkash_views
from django.urls import path, include

from rest_framework.routers import SimpleRouter
router = SimpleRouter(trailing_slash='')

router.register(r'order', views.OrderData, basename='bkash')
urlpatterns = [
    path('get', views.ReturnData.as_view(), name="automation"),
    path('', include(router.urls), name="order_data"),
    path('bkash/callback', bkash_views.bkash_callback, name='bkash-url'),
]
