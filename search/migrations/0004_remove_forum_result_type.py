# Generated by Django 2.2.19 on 2021-04-06 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_flush_discourse_documents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchdocument',
            name='result_type',
            field=models.CharField(choices=[('D', 'Documentation'), ('W', 'Wagtail Page')], max_length=1),
        ),
    ]
