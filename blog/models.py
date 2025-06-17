from django.db import models
from django.contrib.auth.models import User 
# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=200)
    image = models.URLField(null=True, blank=True)
    public_id = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
