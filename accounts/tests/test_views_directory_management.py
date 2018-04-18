from time import time
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from wagtail.wagtailcore.models import Site
from allauth.account.models import EmailAddress
from django_otp.plugins.otp_totp.models import TOTPDevice

from common.tests.utils import (
    turn_on_instance_management,
    turn_on_instance_scanning,
)
from directory.models.settings import DirectorySettings
from directory.tests.factories import DirectoryPageFactory
from directory.models import DirectoryEntry


class FormViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        turn_on_instance_management()
        turn_on_instance_scanning()

        cls.site = Site.objects.get()
        cls.directory = DirectoryPageFactory(
            parent=cls.site.root_page,
        )
        User = get_user_model()
        cls.email = 'email@email.com'
        cls.password = 'password'
        cls.user = User.objects.create_user(username='username', password=cls.password, email=cls.email, is_active=True)
        cls.recipient_group = Group.objects.create(name='Recipient group')
        EmailAddress.objects.create(user=cls.user, email=cls.email, verified=True)
        cls.device = TOTPDevice.objects.create(
            user=cls.user,
            confirmed=True,
            key='2a2bbba1092ffdd25a328ad1a0a5f5d61d7aacc4',
            step=30,
            t0=int(time() - (30 * 3)),
            digits=6,
            tolerance=0,
            drift=0,
        )

    def setUp(self):
        # self.client.force_login(self.user)
        self.client.post(
            reverse('account_login'),
            {'login': self.email, 'password': self.password},
        )
        self.client.post(
            reverse('two-factor-authenticate'),
            # The token below corresponds to the parameters on the
            # device just created.
            {'otp_device': self.device.id, 'otp_token': '154567'},
        )

    @mock.patch('directory.models.pages.scanner')
    def test_sends_email(self, scanner):
        self.directory_settings = DirectorySettings.for_site(self.site)
        self.directory_settings.new_instance_alert_group = self.recipient_group
        self.directory_settings.save()

        User = get_user_model()
        recipient = User.objects.create_user(username='recipient', email='recipient@recipient.com', is_active=True)
        recipient.groups.add(self.recipient_group)

        response = self.client.post(
            reverse('securedroppage_add'),
            {
                'title': 'Page title',
                'landing_page_url': 'https://domain.com',
                'onion_address': 'https://domain.com/domain.onion',
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            }
        )
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [recipient.email])
        self.assertIn('{}/admin/pages/{}/edit/'.format(
            self.site.root_url,
            DirectoryEntry.objects.get().id,
        ), mail.outbox[0].body)

    @mock.patch('directory.models.pages.scanner')
    def test_not_sends_email__no_setting(self, scanner):
        User = get_user_model()
        recipient = User.objects.create_user(username='recipient', email='recipient@recipient.com', is_active=True)
        recipient.groups.add(self.recipient_group)

        response = self.client.post(
            reverse('securedroppage_add'),
            {
                'title': 'Page title',
                'landing_page_url': 'https://domain.com',
                'onion_address': 'https://domain.com/domain.onion',
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            },
        )
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(len(mail.outbox), 0)

    @mock.patch('directory.models.pages.scanner')
    def test_not_sends_email__no_users(self, scanner):
        self.directory_settings = DirectorySettings.for_site(self.site)
        self.directory_settings.new_instance_alert_group = self.recipient_group
        self.directory_settings.save()

        response = self.client.post(
            reverse('securedroppage_add'),
            {
                'title': 'Page title',
                'landing_page_url': 'https://domain.com',
                'onion_address': 'https://domain.com/domain.onion',
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            },
        )
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(len(mail.outbox), 0)
