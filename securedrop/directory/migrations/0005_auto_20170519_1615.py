# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-19 16:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0004_auto_20170519_0637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='securedrop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='directory.Securedrop'),
        ),
    ]
