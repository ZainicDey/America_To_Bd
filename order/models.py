from django.db import models
from django.contrib.auth.models import User
import secrets
import string

def generate_unique_tracker(length=12):
    chars = string.ascii_uppercase + string.digits
    while True:
        tracker = ''.join(secrets.choice(chars) for _ in range(length))
        if not ResolvedOrder.objects.filter(tracker=tracker).exists():
            return tracker
        
# Create your models here.
class OrderRequest(models.Model):
    STATUS_CHOICES = [
        ('PD', 'Pending'),
        ('AC', 'Accepted'),
        ('OC', 'Order Complete')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_url = models.URLField()
    quantity = models.IntegerField()
    description = models.TextField(max_length=300)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ResolvedOrder(models.Model):
    order = models.OneToOneField(OrderRequest, on_delete=models.CASCADE, related_name='ResolvedOrder')
    tracker = models.CharField(blank=True, editable=False, unique=True, max_length=20)
    quantity = models.IntegerField()
    usd_price = models.DecimalField(decimal_places=2, max_digits=10) 
    converted_price = models.DecimalField(decimal_places=2, max_digits=10) 
    custom_fee = models.IntegerField(default=0)
    tax = models.DecimalField(decimal_places=2, max_digits=10) 
    cost = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    # estimated_arrival = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.tracker:
            self.tracker = generate_unique_tracker()
        self.order.status = 'AC'
        self.order.save()
        
        super().save(*args, **kwargs)
        
        if is_new:
            TrackingOrder.objects.create(resolved_order=self, user=self.order.user)
            
    def update_order_status(self, status):
        self.order.status = status
        if status=="PD":
            self.is_paid=True
            self.save()
        self.order.save()

class TrackingOrder(models.Model):
    resolved_order = models.OneToOneField(ResolvedOrder, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    