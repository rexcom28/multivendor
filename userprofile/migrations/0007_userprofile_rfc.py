# Generated by Django 3.2.15 on 2022-11-02 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0006_userprofile_is_vendor'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='RFC',
            field=models.CharField(blank=True, max_length=13),
        ),
    ]