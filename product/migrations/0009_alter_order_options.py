# Generated by Django 5.2.1 on 2025-05-31 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_order_payment_id_order_payment_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at']},
        ),
    ]
