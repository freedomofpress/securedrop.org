# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
<<<<<<< HEAD
        ('landing_page_checker', '0011_move_results_model'),
=======
        ('landing_page_checker', '0011_move_results'),
>>>>>>> Move SecuredropOwner to directory app
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
