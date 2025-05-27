from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=15, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

class Product(models.Model):
    image = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=15)
    description = models.TextField()
    color = models.JSONField(default=list)
    size = models.JSONField(default=list)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='product')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)