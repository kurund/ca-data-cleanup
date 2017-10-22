# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-22 18:28
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('batch_date', models.DateField(verbose_name='Date')),
                ('omr_baseline', models.FileField(upload_to='uploads/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['csv'], 'Please upload valid CSV file')], verbose_name='Baseline')),
                ('omr_self_aware', models.FileField(upload_to='uploads/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['csv'], 'Please upload valid CSV file')], verbose_name='Self Awareness')),
                ('omr_career_aware', models.FileField(upload_to='uploads/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['csv'], 'Please upload valid CSV file')], verbose_name='Career Awareness')),
                ('omr_career_planning', models.FileField(upload_to='uploads/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['csv'], 'Please upload valid CSV file')], verbose_name='Career Planning')),
                ('error_log', models.FileField(blank=True, help_text='Do not upload. This field will be auto updated.', upload_to='uploads/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['log'], 'Please upload valid log file')], verbose_name='Error Log')),
                ('comment', models.TextField(blank=True, max_length=200)),
                ('proc_baseline', models.FileField(blank=True, help_text='Do not upload. This field will be auto updated.', upload_to='data/', validators=[django.core.validators.FileExtensionValidator(['csv'], 'Please upload valid CSV file')], verbose_name='Baseline')),
                ('proc_self_aware', models.FileField(blank=True, help_text='Do not upload. This field will be auto updated.', upload_to='data/', validators=[django.core.validators.FileExtensionValidator(['csv'], 'Please upload valid CSV file')], verbose_name='Self Awareness')),
                ('proc_career_aware', models.FileField(blank=True, help_text='Do not upload. This field will be auto updated.', upload_to='data/', validators=[django.core.validators.FileExtensionValidator(['csv'], 'Please upload valid CSV file')], verbose_name='Career Awareness')),
                ('proc_career_planning', models.FileField(blank=True, help_text='Do not upload. This field will be auto updated.', upload_to='data/', validators=[django.core.validators.FileExtensionValidator(['csv'], 'Please upload valid CSV file')], verbose_name='Career Planning')),
                ('status', models.IntegerField(choices=[(1, 'Not Processed'), (2, 'Baseline Processed'), (3, 'Self Awareness Processed'), (4, 'Career Awareness Processed'), (5, 'Career Planning Processed'), (6, 'Transformation Completed')], default=1, help_text='Do not change. This field will be auto updated.')),
            ],
        ),
    ]
