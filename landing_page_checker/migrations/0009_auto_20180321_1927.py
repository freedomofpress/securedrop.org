# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-21 19:27
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('landing_page_checker', '0008_auto_20171120_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='securedrop',
            field=modelcluster.fields.ParentalKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='results', to='landing_page_checker.SecuredropPage'),
        ),
    ]