from django.test import TestCase

from directory.models.entry import ScanResult
from directory.strings import SEVERE_WARNINGS, MODERATE_WARNINGS


class FailureMessagesTest(TestCase):
    def test_message_attributes(self):
        """warning messages should refer to field names on the ResultState model"""
        names = (
            {x.name for x in ScanResult._meta.get_fields()} -
            {
                'id',
                'securedrop',
                'landing_page_url',
                'live',
                'last_result_seen',
                'grade',
            }
        )

        for attr, _ in SEVERE_WARNINGS:
            self.assertIn(attr, names)
        for attr, _ in MODERATE_WARNINGS:
            self.assertIn(attr, names)
