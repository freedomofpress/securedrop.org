# Generated by Django 2.2.14 on 2020-12-16 17:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0022_scanresult_http2'),
    ]

    operations = [
        migrations.AddField(
            model_name='directoryentry',
            name='onion_name',
            field=models.CharField(blank=True, max_length=255, null=True, validators=[django.core.validators.RegexValidator(message='Enter a valid onion name.', regex='\\.securedrop\\.tor\\.onion$')], verbose_name='SecureDrop onion names'),
        ),
    ]
