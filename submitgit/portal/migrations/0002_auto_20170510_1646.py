# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-10 16:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='repository',
            old_name='user',
            new_name='student',
        ),
    ]
