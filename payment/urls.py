from django.urls import path
from . import bkash_views

# urlpatterns = [
#     path('', views.initiate_payment, name='payment_initiate'),
#     path('success/', views.payment_success, name='payment_success'),
#     path('fail/', views.payment_fail, name='payment_fail'),
#     path('cancel/', views.payment_cancel, name='payment_cancel'),
#     path('ipn/', views.payment_ipn, name='payment_ipn'),
# ]   
urlpatterns = [
    #bkash
    # path('/bkash/start-payment/<int:pk>/', bkash_views.start_payment, name='start-payment'),
    # path('bkash/callback/', views_views.bkash_callback, name='bkash-callback'),

    #nagad
    # path('nagad/start-payment/<int:pk>/', nagad_views.start_nagad_payment, name='start-nagad-payment'),
    # path('nagad/callback/', nagad_views.nagad_callback, name='nagad-callback'),
]