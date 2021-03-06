# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-10 13:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import portal.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField(max_length=5000)),
                ('attachments', models.FileField(blank=True, upload_to='uploads/assignment/%Y/%m/%d/')),
                ('deadline', models.DateTimeField()),
                ('is_test', models.BooleanField(default=False)),
                ('test_file_name', models.CharField(max_length=100)),
                ('test_input', models.TextField(blank=True, max_length=5000)),
                ('test_output', models.TextField(blank=True, max_length=5000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField(max_length=5000)),
                ('year', models.IntegerField()),
                ('semester', models.IntegerField(choices=[(0, '1학기'), (1, '여름 계절학기'), (2, '2학기'), (3, '겨울 계절학기')])),
                ('attachments', models.FileField(blank=True, upload_to='uploads/course/%Y/%m/%d/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_verified', models.BooleanField(default=False)),
                ('url', models.URLField()),
                ('craeted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_passed', models.BooleanField(default=False)),
                ('has_error', models.BooleanField(default=True)),
                ('raw_code', models.FileField(upload_to=portal.models.update_filename)),
                ('code', models.TextField(max_length=5000)),
                ('langid', models.IntegerField(choices=[(0, 'Python'), (1, 'Ruby'), (2, 'Clojure'), (3, 'PHP'), (4, 'Javascript'), (5, 'Scala'), (6, 'Go'), (7, 'C,C++'), (8, 'Java'), (9, 'VB.NET'), (10, 'C#'), (11, 'Bash'), (12, 'Objective-C'), (13, 'MySQL'), (14, 'Perl')])),
                ('errors', models.TextField(blank=True, max_length=5000)),
                ('output', models.TextField(blank=True, max_length=5000)),
                ('time', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.Assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(through='portal.Repository', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assignment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.Course'),
        ),
    ]
