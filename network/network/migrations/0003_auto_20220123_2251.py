# Generated by Django 3.1.5 on 2022-01-23 14:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='created_dt',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
