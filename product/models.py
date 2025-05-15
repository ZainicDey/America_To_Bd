from django.db import models

# Create your models here.
class Color(models.Model):
    name = models.CharField(max_length=15)

class Category(models.Model):
    name = models.CharField(max_length=15)

class Product(models.Model):
    name = models.CharField(max_length=15)
    description = models.TextField()
    color = models.ManyToManyField(Color, related_name='product')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='product')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)