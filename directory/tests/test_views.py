from unittest import mock
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.wagtailcore.models import Site

from directory.forms import ScannerForm, DirectoryForm
from directory.models.pages import SCAN_URL
from directory.tests.factories import DirectoryPageFactory


class ScanViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = DirectoryPageFactory(
            parent=Site.objects.get().root_page,
            scanner_form_text='Scanner form',
            org_details_form_text='Org form text'
        )

    @classmethod
    def setUpClass(cls):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        super(ScanViewTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        del os.environ['RECAPTCHA_TESTING']
        super(ScanViewTest, cls).tearDownClass()

    @mock.patch('directory.forms.DirectoryForm.as_p', return_value='')
    @mock.patch('directory.models.pages.scanner')
    def test_unauthenticated_scan(self, scanner, directory_form_as_p):
        response = self.client.post(
            '{}{}'.format(self.directory.url, SCAN_URL),
            {
                'url': 'https://littleweaverweb.com',
                'g-recaptcha-response': 'PASSED',
            }
        )
        self.assertIsInstance(response.context['submission_form'], DirectoryForm)
        self.assertContains(
            response,
            '<a href="/accounts/login/">Log in</a> to add your Securedrop instance to the directory.',
            status_code=200,
        )
        self.assertTemplateUsed(response, 'landing_page_checker/result.html')
        self.assertTemplateUsed(response, 'directory/_submission_form.html')
        directory_form_as_p.assert_not_called()

    @mock.patch('directory.forms.DirectoryForm.as_p', return_value='')
    @mock.patch('directory.models.pages.scanner')
    def test_authenticated_scan(self, scanner, directory_form_as_p):
        User = get_user_model()
        user = User.objects.create_user(username='username', email='email@email.com', is_active=True)
        self.client.force_login(user)
        response = self.client.post(
            '{}{}'.format(self.directory.url, SCAN_URL),
            {
                'url': 'https://littleweaverweb.com',
                'g-recaptcha-response': 'PASSED',
            }
        )
        self.assertIsInstance(response.context['submission_form'], DirectoryForm)
        self.assertNotContains(
            response,
            '<a href="/accounts/login/">Log in</a> to add your Securedrop instance to the directory.',
            status_code=200,
        )
        self.assertTemplateUsed(response, 'landing_page_checker/result.html')
        self.assertTemplateUsed(response, 'directory/_submission_form.html')
        directory_form_as_p.assert_called_once()
        self.assertEqual(response.context['form_text'], self.directory.org_details_form_text)

    def test_render_scan_form(self):
        response = self.client.get(
            '{}{}'.format(self.directory.url, SCAN_URL),
        )
        self.assertIsInstance(response.context['form'], ScannerForm)
        self.assertTemplateUsed(response, 'directory/scanner_form.html')
        self.assertTemplateUsed(response, 'captcha/widget_nocaptcha.html')
        self.assertTemplateNotUsed(response, 'landing_page_checker/result.html')
        self.assertEqual(response.context['text'], self.directory.scanner_form_text)
