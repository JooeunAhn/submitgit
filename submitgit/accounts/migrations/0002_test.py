# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-08 11:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('langid', models.IntegerField(choices=[(0, 'Python'), (1, 'Ruby'), (2, 'Clojure'), (3, 'PHP'), (4, 'Javascript'), (5, 'Scala'), (6, 'Go'), (7, 'C,C++'), (8, 'Java'), (9, 'VB.NET'), (10, 'C#'), (11, 'Bash'), (12, 'Objective-C'), (13, 'MySQL'), (14, 'Perl')])),
                ('code', models.TextField(max_length=5000)),
                ('errors', models.TextField(max_length=1000)),
                ('output', models.TextField(max_length=5000)),
                ('time', models.FloatField()),
            ],
        ),
    ]
