# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-17 05:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0007_auto_20170516_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='test_langids',
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
    ]
