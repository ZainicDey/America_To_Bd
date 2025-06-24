from django.urls import path,include
from . import views

from rest_framework.routers import SimpleRouter
router = SimpleRouter(trailing_slash='')

router.register(r'order_request', views.OrderRequestViewset, basename='order_request'),
router.register(r'resolved_order', views.ResolveOrderViewset, basename='resolved_order'),
router.register(r'csv_export', views.ResolvedFullList, basename='csv_export')

urlpatterns = [
    path('', include(router.urls)),
    path('tracking/<str:tracker_id>', views.TrackingOrderViewset.as_view(), name='track-order')
]
