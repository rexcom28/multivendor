# Generated by Django 3.2.15 on 2023-01-14 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_auto_20230114_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B')], max_length=100, null=True),
        ),
    ]