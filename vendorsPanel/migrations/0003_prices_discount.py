# Generated by Django 3.2.15 on 2023-04-04 00:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0030_auto_20230312_0008'),
        ('vendorsPanel', '0002_prices_price_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='prices',
            name='discount',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='discountPrice', to='store.discount'),
            preserve_default=False,
        ),
    ]