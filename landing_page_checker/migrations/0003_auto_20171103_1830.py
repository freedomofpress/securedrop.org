# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-03 18:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing_page_checker', '0002_auto_20171103_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='hsts_max_age',
            field=models.NullBooleanField(),
        ),
    ]