# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-22 07:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0009_auto_20170521_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='key',
            field=models.BinaryField(default=b'\x010\xda\xf7\xa6y\x86\x14\xa04J\xcd;\n\xbd:\x95hio\xb1>\xc1\xa6s~\xdd\x89h\x14\x89\xb3'),
            preserve_default=False,
        ),
    ]
