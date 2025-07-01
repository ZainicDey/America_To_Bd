from django.contrib import admin
from .models import MannualPayment, BkashToken
# Register your models here.
admin.site.register(MannualPayment)
# admin.site.register(BkashToken)

@admin.register(BkashToken)
class BkashTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'created_at')  # for list view
    fields = ('token', 'created_at')  # for detail view (optional)
    readonly_fields = ('created_at',)  # recommended if it's auto-set