from django.db import models

# Create your models here.
class MannualPayment(models.Model):
    tracker = models.CharField(max_length=15)
    bank_name = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)