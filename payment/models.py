from django.db import models
from order.models import ResolvedOrder
from django.contrib.auth.models import User
# Create your models here.
class MannualPayment(models.Model):
    tracker = models.CharField(max_length=15)
    bank_name = models.CharField(max_length=100)
    bank_id = models.CharField(max_length=100, null= True)
    transaction_id = models.CharField(max_length=100)
    image = models.URLField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
