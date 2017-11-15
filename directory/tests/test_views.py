from unittest import mock
import os

from django.test import TestCase
from wagtail.wagtailcore.models import Site

from directory.models.pages import SCAN_URL
from directory.tests.factories import DirectoryPageFactory


class ScanViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = DirectoryPageFactory(
            parent=Site.objects.get().root_page,
        )

    @classmethod
    def setUpClass(cls):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        super(ScanViewTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        del os.environ['RECAPTCHA_TESTING']
        super(ScanViewTest, cls).tearDownClass()

    @mock.patch('directory.models.pages.scanner')
    def test_unauthenticated(self, scanner):
        response = self.client.post(
            '{}{}'.format(self.directory.url, SCAN_URL),
            {
                'url': 'https://littleweaverweb.com',
                'g-recaptcha-response': 'PASSED',
            }
        )
        self.assertContains(
            response,
            '<a href="/accounts/login/">Log in</a> to add your Securedrop instance to the directory.',
            status_code=200,
        )
        self.assertTemplateUsed(response, 'landing_page_checker/result.html')
        self.assertTemplateUsed(response, 'directory/_submission_form.html')
