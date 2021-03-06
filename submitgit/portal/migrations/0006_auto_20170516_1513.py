# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-16 15:13
from __future__ import unicode_literals

from django.db import migrations, models
import portal.models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0005_auto_20170516_0814'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='test_time',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='raw_code',
            field=models.FileField(blank=True, upload_to=portal.models.update_filename),
        ),
    ]
