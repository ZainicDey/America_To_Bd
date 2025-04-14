from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'order_request', views.OrderRequestViewset)
router.register(r'resolve_order', views.ResolveOrderViewset)
urlpatterns = [
    path('', include(router.urls)),
    path('tracking/<str:tracker_id>/', views.TrackingOrderViewset.as_view(), name='tracking-order'),
]
