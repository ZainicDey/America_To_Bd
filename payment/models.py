from django.db import models
from order.models import ResolvedOrder
from django.contrib.auth.models import User
import cloudinary
import cloudinary.uploader
from django.conf import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

# Create your models here.
class MannualPayment(models.Model):
    tracker = models.CharField(max_length=15)
    bank_name = models.CharField(max_length=100)
    bank_id = models.CharField(max_length=100, null=True)
    transaction_id = models.CharField(max_length=100)
    image = models.URLField(max_length=200, null=True)
    public_id = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def delete(self, *args, **kwargs):
        if self.public_id:
            cloudinary.uploader.destroy(self.public_id, invalidate=True)
        super().delete(*args, **kwargs)


class BkashToken(models.Model):
    token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



# 01770618575
# * 01770618575
# * 01929918378
# * 01770618576
# •01877722345
# * 01619777282
# * 01619777283
# otp: 123456
# pin: 12121