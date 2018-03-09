from time import time
from unittest import mock
import os

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.test import TestCase
from wagtail.wagtailcore.models import Site
from allauth.account.models import EmailAddress
from django_otp.plugins.otp_totp.models import TOTPDevice

from common.tests.utils import (
    turn_on_instance_management,
    turn_on_instance_scanning,
)
from directory.forms import ScannerForm
from directory.models.pages import SCAN_URL
from directory.tests.factories import DirectoryPageFactory
from landing_page_checker.forms import SecuredropPageForm


class ScanViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        turn_on_instance_management()
        turn_on_instance_scanning()

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

    @mock.patch('directory.models.pages.SecuredropPageForm.as_p', return_value='')
    @mock.patch('directory.models.pages.scanner')
    def test_unauthenticated_scan(self, scanner, directory_form_as_p):
        response = self.client.post(
            '{}{}'.format(self.directory.url, SCAN_URL),
            {
                'url': 'https://littleweaverweb.com',
                'g-recaptcha-response': 'PASSED',
            }
        )
        self.assertIsInstance(response.context['submission_form'], SecuredropPageForm)
        self.assertContains(
            response,
            '<a href="/accounts/login/">Log in</a> to add your Securedrop instance to the directory.',
            status_code=200,
        )
        self.assertTemplateUsed(response, 'landing_page_checker/result.html')
        self.assertTemplateUsed(response, 'directory/_submission_form.html')
        directory_form_as_p.assert_not_called()

    @mock.patch('directory.models.pages.SecuredropPageForm.as_p', return_value='')
    @mock.patch('directory.models.pages.scanner')
    def test_verified_scan(self, scanner, directory_form_as_p):
        User = get_user_model()
        email = 'email@email.com'
        user = User.objects.create_user(username='username', email=email, is_active=True, password='password')
        EmailAddress.objects.create(user=user, email=email, verified=True)
        device = TOTPDevice.objects.create(
            user=user,
            confirmed=True,
            key='2a2bbba1092ffdd25a328ad1a0a5f5d61d7aacc4',
            step=30,
            t0=int(time() - (30 * 3)),
            digits=6,
            tolerance=0,
            drift=0,
        )

        self.client.post(
            reverse_lazy('account_login'),
            {'login': 'email@email.com', 'password': 'password'},
        )
        self.client.post(
            reverse_lazy('two-factor-authenticate'),
            # The token below corresponds to the parameters on the
            # device just created.
            {'otp_device': device.id, 'otp_token': '154567'},
        )
        response = self.client.post(
            '{}{}'.format(self.directory.url, SCAN_URL),
            {
                'url': 'https://littleweaverweb.com',
                'g-recaptcha-response': 'PASSED',
            }
        )
        submission_form = response.context['submission_form']
        self.assertIsInstance(submission_form, SecuredropPageForm)
        self.assertNotIn('add_owner', submission_form.fields)
        self.assertNotIn('remove_owner', submission_form.fields)
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
