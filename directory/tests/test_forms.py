from django.test import TestCase

from directory.forms import DirectoryForm
from directory.tests.factories import DirectoryPageFactory
from landing_page_checker.tests.factories import SecuredropPageFactory


class DirectoryFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = DirectoryPageFactory()
        cls.securedrop_page = SecuredropPageFactory(parent=cls.directory)

    def test_validate_unique_title__invalid(self):
        # Make a form that has just a duplicate title, then verify that it
        # causes a validation error.
        form = DirectoryForm(
            data={
                'title': self.securedrop_page.title,
                'landing_page_domain': self.securedrop_page.landing_page_domain + 'm',
                'onion_address': self.securedrop_page.onion_address + 'm.onion',
                'languages_accepted': 'null',
                'topics': 'null',
                'countries': 'null',
            },
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(list(form.errors.keys()), ['title'])
        self.assertEqual(list(form.errors['title']), ['Securedrop page with this Organization name already exists.'])

    def test_validate_unique_title__valid(self):
        # A form without a duplicate title should validate fine.
        form = DirectoryForm(
            data={
                'title': self.securedrop_page.title + 'm',
                'landing_page_domain': self.securedrop_page.landing_page_domain + 'm',
                'onion_address': self.securedrop_page.onion_address + 'm.onion',
                'languages_accepted': 'null',
                'topics': 'null',
                'countries': 'null',
            },
        )

        self.assertTrue(form.is_valid())
