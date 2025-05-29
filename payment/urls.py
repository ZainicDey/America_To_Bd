from django.urls import path,include
from . import bkash_views
from . import mannualpay_views

from rest_framework.routers import SimpleRouter
router = SimpleRouter(trailing_slash='')
router.register(r'mannual-payment', mannualpay_views.MannualPaymentView, basename='mannual-payment')

# urlpatterns = [
#     path('', views.initiate_payment, name='payment_initiate'),
#     path('success/', views.payment_success, name='payment_success'),
#     path('fail/', views.payment_fail, name='payment_fail'),
#     path('cancel/', views.payment_cancel, name='payment_cancel'),
#     path('ipn/', views.payment_ipn, name='payment_ipn'),
# ]   

urlpatterns = [
    #bkash
    path('bkash/start-payment/<str:tracker>', bkash_views.start_payment, name='start-payment'),
    path('bkash/callback', bkash_views.bkash_callback, name='bkash-callback'),
    path('', include(router.urls)),
    #nagad
    # path('nagad/start-payment/<int:pk>/', nagad_views.start_nagad_payment, name='start-nagad-payment'),
    # path('nagad/callback/', nagad_views.nagad_callback, name='nagad-callback'),

    #mannual payment    
    path('approve-payment', mannualpay_views.ApprovePaymentView.as_view(), name='approve-payment'),
]