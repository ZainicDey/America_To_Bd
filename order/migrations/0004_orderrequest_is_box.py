# Generated by Django 5.0.7 on 2025-05-03 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_resolvedorder_box_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderrequest',
            name='is_box',
            field=models.BooleanField(default=False),
        ),
    ]
