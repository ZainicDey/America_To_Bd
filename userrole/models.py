from django.db import models
from django.contrib.auth.models import User
User._meta.get_field('email')._unique = True
# Create your models here.

class UserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userinfo')
    phone = models.CharField(max_length=11, unique=True)
    def __str__(self):
        return self.user.username

