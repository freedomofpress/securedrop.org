from django.test import TestCase

from ivf import utils


class VerificationUtilityTest(TestCase):
    def test_https_is_in_url(self):
        self.assertTrue(utils.validate_https('https://example.com'))

    def test_https_is_not_in_url(self):
        self.assertFalse(utils.validate_https('example.com'))

    def test_onion_link_is_in_href(self):
        pass

    def test_onion_link_is_not_in_href(self):
        pass

    def test_url_does_not_have_subdomain(self):
        self.assertFalse(utils.validate_subdomain('https://example.com/securedrop'))

    def test_url_does_have_subdomain(self):
        self.assertTrue(utils.validate_subdomain('https://securedrop.example.com'))
