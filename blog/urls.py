from django.urls import path,include
from . import views

from rest_framework.routers import SimpleRouter
router = SimpleRouter(trailing_slash='')

router.register(r'post', views.BlogView),

urlpatterns = [
    path('', include(router.urls)),
]
