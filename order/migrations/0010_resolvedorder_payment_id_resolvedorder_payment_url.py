# Generated by Django 5.2.1 on 2025-05-20 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_alter_resolvedorder_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='resolvedorder',
            name='payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='resolvedorder',
            name='payment_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
