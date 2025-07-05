from django.db import models
from django.contrib.auth.models import User
import secrets
import string
from userrole.models import Address
from django.utils import timezone
from resend import Emails
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
    product_url = models.CharField(max_length=1000, blank=True, null=True)
    quantity = models.IntegerField()
    is_box = models.BooleanField(default=False)
    description = models.TextField(max_length=300)
    address = models.ForeignKey(Address, related_name='order_request', on_delete=models.SET_NULL, null=True)
    from_us = models.BooleanField(default=False, null=True, blank=True)

    is_canceled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class ResolvedOrder(models.Model):
    STATUS_CHOICES = [
        ('AC', 'Accepted'),
        ('CN', 'Canceled'),
        ('PD', 'Payment Done'),
        ('SP', 'Shipped in USA'),
        ('OB', 'On Board for BD'),
        ('LB', 'Landed in BD'),
        ('RD', 'Ready to Delivery'),
        ('RF', 'Refunded'),
        ('DD', 'Delivery Done')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_url = models.CharField(max_length=1000, blank=True, null=True)
    tracker = models.CharField(blank=True, editable=False, unique=True, max_length=20)
    quantity = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    usd_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True) 
    converted_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True) 
    custom_fee = models.IntegerField(default=0, blank=True, null=True)
    weight_fee = models.IntegerField(default=0, blank=True, null=True)
    tax = models.DecimalField(decimal_places=2, max_digits=10, default=0, blank=True, null=True)
    box_fee = models.IntegerField(default=0, blank=True, null=True)
    address = models.ForeignKey(Address, related_name='resolved_order', on_delete=models.SET_NULL, null=True)
    discount = models.IntegerField(default=0, blank=True, null=True)
    platform_fee = models.IntegerField(default=0, blank=True, null=True)
    cost = models.IntegerField()
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='AC')
    from_us = models.BooleanField(default=False, null=True, blank=True)

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
            self.track_status.is_canceled = False
            self.track_status.is_shipped = False
            self.track_status.is_on_board = False
            self.track_status.is_landed_in_bd = False
            self.track_status.is_ready_to_delivery = False
            self.track_status.is_received = False
    
            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [self.user.email],
                "subject": "Payment Confirmation - America to BD",
                "html": f"""
                <h2>Your payment is confirmed!</h2>
                <p>Dear {self.user.first_name} {self.user.last_name},</p>
                <p>Your order is being processed now. To download your invoice please check your dashboard.</p>
                <p>You can track your order status using your tracking ID.</p>
                <p><strong>Tracking ID:</strong> {self.tracker}</p>
                <p>Thank you for choosing America to BD!</p>
                """
            })

        elif status == "CN":
            self.track_status.is_canceled = True
            self.track_status.canceled_time = timezone.now()
            self.track_status.is_paid = False
            self.track_status.is_shipped = False
            self.track_status.is_on_board = False
            self.track_status.is_landed_in_bd = False
            self.track_status.is_ready_to_delivery = False
            self.track_status.is_received = False

            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [self.user.email],
                "subject": "Payment Cancelled - America to BD",
                "html": f"""
                <h2>Your payment is cancelled</h2>
                <p>Dear {self.user.first_name} {self.user.last_name},</p>
                <p><strong>Order ID:</strong> {self.tracker}</p>
                <p>Your order is cancelled. Please contact our support team for more details.</p>
                """
            })
        elif status == "SP":
            self.track_status.is_paid = True
            self.track_status.is_shipped = True
            self.track_status.shipped_in_usa_time = timezone.now()
            self.track_status.is_canceled = False
            self.track_status.is_on_board = False
            self.track_status.is_landed_in_bd = False
            self.track_status.is_ready_to_delivery = False
            self.track_status.is_received = False

            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [self.user.email],
                "subject": "Your order is shipped in USA - America to BD",
                "html": f"""
                <h2>Your order {self.tracker} is shipped. Will be delivered soon.</h2>
                <p>Dear {self.user.first_name} {self.user.last_name},</p>
                <p>Your order is being prepared for shipment to Bangladesh.</p>
                <p><strong>Tracking ID:</strong> {self.tracker}</p>
                <p>Thank you for choosing America to BD!</p>
                """
            })
        elif status == "OB":
            self.track_status.is_paid = True
            self.track_status.is_shipped_in_usa = True
            self.track_status.is_on_board = True
            self.track_status.on_board_time = timezone.now()
            self.track_status.is_canceled = False
            self.track_status.is_landed_in_bd = False
            self.track_status.is_ready_to_delivery = False
            self.track_status.is_received = False

        elif status == "RF":
            self.track_status.is_refunded = True
            self.track_status.is_paid = False
            self.track_status.is_shipped_in_usa = False
            self.track_status.is_on_board = False
            self.track_status.is_landed_in_bd = False
            self.track_status.is_ready_to_delivery = False
            self.track_status.is_received = False
            self.track_status.refunded_time = timezone.now()

        elif status == "LB":
            self.track_status.is_paid = True
            self.track_status.is_shipped_in_usa = True
            self.track_status.is_on_board = True
            self.track_status.is_landed_in_bd = True
            self.track_status.landed_in_bd_time = timezone.now()
            self.track_status.is_canceled = False
            self.track_status.is_ready_to_delivery = False
            self.track_status.is_received = False

        elif status == "RD":
            self.track_status.is_paid = True
            self.track_status.is_shipped_in_usa = True
            self.track_status.is_on_board = True
            self.track_status.is_landed_in_bd = True
            self.track_status.is_ready_to_delivery = True
            self.track_status.ready_to_delivery_time = timezone.now()
            self.track_status.is_received = False
            self.track_status.is_canceled = False

            Emails.send({
                "from": "America to BD <noreply@americatobd.com>",
                "to": [self.user.email],
                "subject": "Your order is ready to deliver - America to BD",
                "html": f"""
                <h2>Your order {self.tracker} will be delivered soon.</h2>
                <p>Dear {self.user.first_name} {self.user.last_name},</p>
                <p>Thank you for choosing America to BD!</p>
                """
            })
            
        elif status == "DD":
            self.track_status.is_paid = True
            self.track_status.is_shipped_in_usa = True
            self.track_status.is_received = True
            self.track_status.received_time = timezone.now()
            self.track_status.is_canceled = False
            self.track_status.is_ready_to_delivery = True
            self.track_status.is_landed_in_bd = True
            self.track_status.is_on_board = True

        self.save()
        self.track_status.save()

    class Meta:
        ordering = ['-created_at']

class TrackingOrder(models.Model):
    resolved_order = models.OneToOneField(ResolvedOrder, on_delete=models.CASCADE, related_name='track_status')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    is_canceled = models.BooleanField(default=False)
    canceled_time = models.DateTimeField(blank=True, null=True)

    is_paid = models.BooleanField(default=False)
    paid_time = models.DateTimeField(blank=True, null=True)

    is_shipped_in_usa = models.BooleanField(default=False)
    shipped_in_usa_time = models.DateTimeField(blank=True, null=True)

    is_on_board = models.BooleanField(default=False)
    on_board_time = models.DateTimeField(blank=True, null=True)

    is_landed_in_bd = models.BooleanField(default=False)
    landed_in_bd_time = models.DateTimeField(blank=True, null=True)   

    is_ready_to_delivery = models.BooleanField(default=False)
    ready_to_delivery_time = models.DateTimeField(blank=True, null=True)

    is_received = models.BooleanField(default=False)
    received_time = models.DateTimeField(blank=True, null=True)
    
    is_refunded = models.BooleanField(default=False)
    refunded_time = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)