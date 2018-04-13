# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('landing_page_checker', '0011_move_results'),
    ]

    database_operations = [
        migrations.AlterModelTable('SecuredropOwner', 'directory_securedropowner'),
    ]

    state_operations = [
        migrations.DeleteModel('SecuredropOwner'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations
        )
    ]
