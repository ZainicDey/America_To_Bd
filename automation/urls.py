from . import views
from django.urls import path, include

urlpatterns = [
    path('get', views.ReturnData.as_view(), name="automation")
]
