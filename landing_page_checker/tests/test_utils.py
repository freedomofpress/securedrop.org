from unittest import TestCase

from landing_page_checker.utils import url_to_domain


class URLToDomainTestCase(TestCase):
    def test_url_to_domain_strips_protocol(self):
        url = 'https://securedrop.org'
        self.assertEqual(url_to_domain(url), 'securedrop.org')

    def test_url_to_domain_strips_path(self):
        url = 'securedrop.org/path/'
        self.assertEqual(url_to_domain(url), 'securedrop.org')

    def test_url_to_domain_strips_path_and_protocol(self):
        url = 'https://securedrop.org/path/'
        self.assertEqual(url_to_domain(url), 'securedrop.org')
