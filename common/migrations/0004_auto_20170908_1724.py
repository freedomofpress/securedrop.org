# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-08 17:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_auto_20170830_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='button',
            name='text',
            field=models.CharField(default='Default', max_length=50),
            preserve_default=False,
        ),
    ]
