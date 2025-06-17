from django.db import models
from django.contrib.auth.models import User

User._meta.get_field('email')._unique = True
# Create your models here.

class UserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userinfo')
    phone = models.CharField(
        max_length=20,
        unique=True,
    )
    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='address', null=True)
    district = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    road = models.TextField(max_length=100)
    post = models.CharField(max_length=30)
    