from django.db import models
from django.contrib.auth.models import User
import secrets
import string
# from userrole.models import Address

def generate_unique_tracker(length=12):
    chars = string.ascii_uppercase + string.digits
    while True:
        tracker = ''.join(secrets.choice(chars) for _ in range(length))
        if not ResolvedOrder.objects.filter(tracker=tracker).exists():
            return tracker
        
# Create your models here.
class OrderRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_url = models.URLField()
    quantity = models.IntegerField()
    # address
    # is_box = models.BooleanField(default=False)
    description = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ResolvedOrder(models.Model):
    STATUS_CHOICES = [
        ('AC', 'Accepted'),
        ('CN', 'Canceled'),
        ('PD', 'Payment Done'),
        ('SP', 'Shipped')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_url = models.URLField()
    tracker = models.CharField(blank=True, editable=False, unique=True, max_length=20)
    quantity = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    usd_price = models.DecimalField(decimal_places=2, max_digits=10) 
    converted_price = models.DecimalField(decimal_places=2, max_digits=10) 
    custom_fee = models.IntegerField(default=0)
    tax = models.DecimalField(decimal_places=2, max_digits=10) 
    # box_fee = models.IntegerField(default=0, blank=True, null=True)
    # address = models.OneToOneField(Address, related_name='Resolved_order')
    cost = models.IntegerField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='AC')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.tracker:
            self.tracker = generate_unique_tracker()
        
        super().save(*args, **kwargs)
        
        if is_new:
            TrackingOrder.objects.create(resolved_order=self, user=self.user)
            
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
    