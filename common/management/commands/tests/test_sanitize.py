from django.test import SimpleTestCase

from fpfwagtailcommon.utils.management.commands.sanitize_base import get_model

from common.management.commands.sanitize import Command


# This test exists so that if any of the model paths in the sanitize management
# command's profile changes, the test will fail so that they're updated there too.
class TestSanitizeProfile(SimpleTestCase):
    def test_truncate_labels_resolve(self):
        for label in Command.profile.truncate_tables:
            with self.subTest(label=label):
                get_model(label)

    def test_mangle_labels_and_fields_resolve(self):
        for label, updates in Command.profile.mangle_tables.items():
            model = get_model(label)
            for field_name in updates:
                with self.subTest(label=label, field=field_name):
                    model._meta.get_field(field_name)
