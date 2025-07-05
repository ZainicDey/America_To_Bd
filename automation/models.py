from django.db import models 
from django.contrib.auth.models import User
from userrole.models import Address
# Create your models here.
class AutomatedOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('due', 'Due'),
        ('accepted', 'Payment Accepted'),
        ('delivered', 'Delivered')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automated_orders')

    title = models.CharField(max_length=1000)
    image = models.CharField(max_length=1000)
    price = models.FloatField()
    url = models.CharField(max_length=1000, null=True, blank=True)

    #before order
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True, related_name="automated_orders")
    us_tax = models.CharField(max_length=10, default="8.87%", null=True, blank=True)
    us_tax_amount_in_usd = models.FloatField(default=0.0, null=True, blank=True)
    us_total = models.FloatField(default=0.0, null=True, blank=True)
    dollar_rate = models.FloatField(default=125.0, null=True, blank=True)
    bdt_total = models.IntegerField(default=0.0, null=True, blank=True)
    tax = models.DecimalField(decimal_places=2, max_digits=10, default=8.87) #from resolved order

    #after order
    quantity = models.IntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    # usd_price = models.DecimalField(decimal_places=2, max_digits=10) <= already in us total
    custom_fee = models.IntegerField(default=0)
    weight_fee = models.IntegerField(default=0, blank=True, null=True)
    box_fee = models.IntegerField(default=0, blank=True, null=True)
    discount = models.IntegerField(default=0, blank=True, null=True)
    platform_fee = models.IntegerField(default=0, blank=True, null=True)
    due = models.IntegerField(default=0, blank=True, null=True) #due conditional

    cost = models.IntegerField(default=0, blank=True, null=True)
    status = models.CharField(max_length=10, default='due', choices=STATUS_CHOICES)

    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_url = models.CharField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)