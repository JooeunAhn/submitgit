# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-08 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_test'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='errors',
            field=models.TextField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='test',
            name='output',
            field=models.TextField(blank=True, max_length=5000),
        ),
    ]