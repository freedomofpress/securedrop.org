from django.test import TestCase
from django.urls import reverse
from wagtail.core.models import Site

from directory.tests.factories import (
    DirectoryPageFactory,
    DirectoryEntryFactory,
)


class ApiTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = DirectoryPageFactory(
            parent=Site.objects.get().root_page,
        )
        cls.entry = DirectoryEntryFactory(parent=cls.directory)

    def test_directory_is_at_api_root(self):
        response = self.client.get(reverse('api-root'), format='json')

        self.assertIn('directory', response.data)

    def test_directory_entry_data_is_correct(self):
        response = self.client.get(reverse('directoryentry-list'), format='json')

        self.assertEqual(dict(response.data[0]), {
            'title': self.entry.title,
            'slug': self.entry.slug,
            'directory_url': self.entry.full_url,
            'first_published_at': self.entry.first_published_at,
            'landing_page_url': self.entry.landing_page_url,
            'onion_address': self.entry.onion_address,
            'organization_logo': self.entry.organization_logo,
            'organization_description': self.entry.organization_description,
            'organization_url': self.entry.organization_url,
            'countries': [country.title for country in self.entry.countries.all()],
            'topics': [topic.title for topic in self.entry.topics.all()],
            'languages': [lang.title for lang in self.entry.languages.all()],
        })
