# Generated by Django 3.2.15 on 2023-01-15 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0023_alter_product_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]