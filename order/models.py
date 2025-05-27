from django.db import models
from django.contrib.auth.models import User
import secrets
import string
from userrole.models import Address
from django.utils import timezone
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
    product_url = models.URLField(max_length=1000)
    quantity = models.IntegerField()
    is_box = models.BooleanField(default=False)
    description = models.TextField(max_length=300)
    address = models.ForeignKey(Address, related_name='order_request', on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class ResolvedOrder(models.Model):
    STATUS_CHOICES = [
        ('AC', 'Accepted'),
        ('CN', 'Canceled'),
        ('PD', 'Payment Done'),
        ('SP', 'Shipped'),
        ('UR', 'User Received')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_url = models.URLField(max_length=1000)
    tracker = models.CharField(blank=True, editable=False, unique=True, max_length=20)
    quantity = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    usd_price = models.DecimalField(decimal_places=2, max_digits=10) 
    converted_price = models.DecimalField(decimal_places=2, max_digits=10) 
    custom_fee = models.IntegerField(default=0)
    tax = models.DecimalField(decimal_places=2, max_digits=10) 
    box_fee = models.IntegerField(default=0, blank=True, null=True)
    address = models.ForeignKey(Address, related_name='resolved_order', on_delete=models.SET_NULL, null=True)
    discount = models.IntegerField(default=0, blank=True, null=True)
    platform_fee = models.IntegerField(default=0, blank=True, null=True)
    cost = models.IntegerField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='AC')

    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_url = models.CharField(blank=True, null=True)

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
        valid_statuses = dict(self.STATUS_CHOICES).keys()
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'")

        self.status = status 

        if status == "PD":
            self.track_status.is_paid = True
            self.track_status.paid_time = timezone.now()
            self.track_status.is_shipped = False
            self.track_status.is_received = False
        elif status == "CN":
            pass
        elif status == "SP":
            self.track_status.is_paid = True
            self.track_status.is_shipped = True
            self.track_status.shipped_time = timezone.now()
            self.track_status.is_received = False
        elif status == "UR":
            self.track_status.is_paid = True
            self.track_status.is_shipped = True
            self.track_status.is_received = True
            self.track_status.received_time = timezone.now()

        self.save()
        self.track_status.save()

    class Meta:
        ordering = ['-created_at']

class TrackingOrder(models.Model):
    resolved_order = models.OneToOneField(ResolvedOrder, on_delete=models.CASCADE, related_name='track_status')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    is_paid = models.BooleanField(default=False)
    paid_time = models.DateTimeField(blank=True, null=True)

    is_shipped = models.BooleanField(default=False)
    shipped_time = models.DateTimeField(blank=True, null=True)

    is_received = models.BooleanField(default=False)
    received_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)