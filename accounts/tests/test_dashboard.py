from time import time

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from allauth.account.models import EmailAddress
from django_otp.plugins.otp_totp.models import TOTPDevice
from wagtail.core.models import Site

from common.tests.utils import (
    turn_on_instance_management,
    turn_on_instance_scanning,
)
from directory.models import SCAN_URL
from directory.tests.factories import DirectoryPageFactory


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

    def test_create_url(self):
        User = get_user_model()
        name = 'username'
        email = 'email@email.com'
        password = 'whatever'
        user = User.objects.create_user(username=name, email=email, is_active=True, password=password)
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
            {'login': email, 'password': password},
        )
        self.client.post(
            reverse_lazy('two-factor-authenticate'),
            # The token below corresponds to the parameters on the
            # device just created.
            {'otp_device': device.id, 'otp_token': '154567'},
        )
        response = self.client.get(reverse_lazy('dashboard'))
        expected_create_url = '{}{}'.format(self.directory.url, SCAN_URL)
        self.assertEqual(
            response.context['create_link'],
            expected_create_url
        )
