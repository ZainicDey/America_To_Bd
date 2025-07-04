# Generated by Django 5.2.1 on 2025-05-27 17:30

import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('address', models.CharField(max_length=500)),
                ('tracker', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('totalPrice', models.IntegerField()),
                ('status', models.CharField(choices=[('Pending', 'User Sent'), ('Cancel', 'Admin Canceled'), ('Accept', 'Payment Accepted'), ('Received', 'User Received')], default='Pending', max_length=11)),
                ('contactNo', models.CharField(max_length=11, validators=[django.core.validators.MinLengthValidator(11)])),
                ('email', models.EmailField(max_length=254)),
                ('transactionId', models.CharField(max_length=50)),
                ('payMethod', models.CharField(max_length=11)),
                ('shippingMethod', models.CharField(max_length=20)),
                ('shippingCost', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.URLField(blank=True, null=True)),
                ('name', models.CharField(max_length=15)),
                ('description', models.TextField()),
                ('color', models.JSONField(default=list)),
                ('size', models.JSONField(default=list)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product', to='product.category')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('color', models.CharField(max_length=50)),
                ('size', models.CharField(max_length=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='product.order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orderItem', to='product.product')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order', to='product.product'),
        ),
    ]
