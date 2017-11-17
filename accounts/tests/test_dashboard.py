from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy

from wagtail.wagtailcore.models import Site

from directory.models import SCAN_URL
from directory.tests.factories import DirectoryPageFactory


class ScanViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = DirectoryPageFactory(
            parent=Site.objects.get().root_page,
            scanner_form_text='Scanner form',
            org_details_form_text='Org form text'
        )

    def test_create_url(self):
        User = get_user_model()
        user = User.objects.create_user(username='username', email='email@email.com', is_active=True)
        self.client.force_login(user)
        response = self.client.get(reverse_lazy('dashboard'))
        expected_create_url = '{}{}'.format(self.directory.url, SCAN_URL)
        self.assertEqual(
            response.context['create_link'],
            expected_create_url
        )
