# Generated by Django 5.0.7 on 2025-04-30 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resolvedorder',
            name='status',
            field=models.CharField(choices=[('AC', 'Accepted'), ('CN', 'Canceled'), ('PD', 'Payment Done'), ('SP', 'Shipped')], default='AC', max_length=2),
        ),
    ]
