# Generated by Django 3.1.4 on 2021-01-08 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20210108_2211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='winner',
        ),
    ]