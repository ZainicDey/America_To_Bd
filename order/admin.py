from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.OrderRequest)
admin.site.register(models.ResolvedOrder)
admin.site.register(models.TrackingOrder)