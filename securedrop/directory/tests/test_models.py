from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase

from directory.models import Securedrop


class SecuredropTest(TestCase):
    def test_securedrop_can_save_expected_urls(self):
        securedrop = Securedrop(organization='Freedom of the Press Foundation',
                                landing_page_domain='freedom.press',
                                onion_address='notreal.onion')
        securedrop.save()
        self.assertIn(securedrop, Securedrop.objects.all())

    def test_securedrop_cannot_save_empty_urls(self):
        securedrop = Securedrop()
        with self.assertRaises(ValidationError):
            securedrop.save()
            securedrop.full_clean()

    def test_duplicate_securedrops_are_invalid(self):
        securedrop1 = Securedrop(organization='Freedom of the Press Foundation',
                                landing_page_domain='freedom.press',
                                onion_address='notreal.onion')
        securedrop1.save()
        securedrop2 = Securedrop(organization='Freedom of the Press Foundation',
                                landing_page_domain='freedom.press',
                                onion_address='notreal.onion')
        with self.assertRaises(IntegrityError):
            securedrop2.save()
