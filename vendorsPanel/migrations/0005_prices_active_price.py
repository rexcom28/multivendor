# Generated by Django 3.2.15 on 2023-04-09 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendorsPanel', '0004_remove_prices_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='prices',
            name='active_price',
            field=models.BooleanField(default=False),
        ),
    ]