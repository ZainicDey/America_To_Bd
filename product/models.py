from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
import uuid
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)

class Product(models.Model):
    image = models.JSONField(default=list, null=True, blank=True) 
    public_id = models.JSONField(default=list, null=True, blank=True)
    name = models.CharField(max_length=1000)
    description = models.TextField()
    color = models.JSONField(default=list, null=True, blank=True)
    size = models.JSONField(default=list, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='product')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'User Sent'),
        ('Canceled', 'Admin Canceled'), 
        ('Accepted', 'Payment Accepted'),
        ('Received', 'User Received')
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='order')
    address = models.CharField(max_length=500)
    tracker = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    totalPrice = models.IntegerField()
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='Pending') # Changed default to 'Pending'
    contactNo = models.CharField(max_length=11, validators=[
            MinLengthValidator(11),
        ])
    email = models.EmailField(max_length=254)
    transactionId = models.CharField(max_length=50, null=True, blank=True)
    payMethod = models.CharField(max_length=11, null=True, blank=True)
    shippingMethod = models.CharField(max_length=20, null=True, blank=True)
    shippingCost = models.IntegerField()

    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_url = models.CharField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.tracker}"
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, to_field='tracker')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='orderItem')
    quantity = models.IntegerField()
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem for {self.order.tracker}"