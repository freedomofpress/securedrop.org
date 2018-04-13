# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('landing_page_checker', '0012_move_securedrop_owner'),
    ]

    database_operations = [
        migrations.AlterModelTable('SecuredropPage', 'directory_securedroppage'),
    ]

    state_operations = [
        migrations.DeleteModel('SecuredropPage'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
