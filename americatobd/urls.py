"""
URL configuration for americatobd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from invoice.views import generate_invoice_pdf
from resetpassword import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userrole.urls')),
    path('order/', include('order.urls')),
    path('payment/', include('payment.urls')),
    path('product/', include('product.urls')),
    path('invoice/<str:tracker>', generate_invoice_pdf, name='generate_invoice_pdf'),
    path('blog/', include('blog.urls')),
    path('contact/', include('contact.urls')),

    path(
        "request-password-reset",
        views.PasswordReset.as_view(),
        name="request-password-reset",
    ),
    path(
        "password-reset/<str:encoded_pk>/<str:token>/",
        views.ResetPasswordAPI.as_view(),
        name="reset-password",
    ),
]
