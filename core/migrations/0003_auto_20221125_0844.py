# Generated by Django 3.2.15 on 2022-11-25 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_product_inventory_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment_detail',
            name='order_id',
        ),
        migrations.RemoveField(
            model_name='product_inventory',
            name='product_id',
        ),
        migrations.DeleteModel(
            name='Discount',
        ),
        migrations.DeleteModel(
            name='Payment_Detail',
        ),
        migrations.DeleteModel(
            name='Product_Inventory',
        ),
    ]
