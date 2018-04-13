from django.test import TestCase

from directory.tests.factories import DirectoryPageFactory
from landing_page_checker.forms import LandingPageForm, SecuredropPageForm
from directory.tests.factories import SecuredropPageFactory


class LandingPageFormTest(TestCase):
    def test_form_validation(self):
        test_landing_page_form = LandingPageForm({'url': 'https://example.com/securedrop'})
        self.assertEqual(test_landing_page_form.is_valid(), True)

    def test_form_url_input_has_css_classes(self):
        form = LandingPageForm()
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_validation_for_blank_url(self):
        form = LandingPageForm(data={'url': ''})
        self.assertFalse(form.is_valid())

    def test_form_validation_for_not_a_url(self):
        form = LandingPageForm(data={'url': 'pizza'})
        self.assertFalse(form.is_valid())


class SecuredropPageFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.directory = DirectoryPageFactory()
        cls.securedrop_page = SecuredropPageFactory(parent=cls.directory)

    def test_validate_unique_title__invalid(self):
        # Make a form that has just a duplicate title, then verify that it
        # causes a validation error.
        form = SecuredropPageForm(
            directory_page=self.directory,
            data={
                'title': self.securedrop_page.title,
                'landing_page_domain': self.securedrop_page.landing_page_domain + 'm',
                'onion_address': self.securedrop_page.onion_address + 'm.onion',
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            },
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(list(form.errors.keys()), ['title'])
        self.assertEqual(list(form.errors['title']), ['Securedrop page with this Organization name already exists.'])

    def test_validate_unique_title__valid__same_instance(self):
        # Make a form that has just a duplicate title, then verify that it
        # causes a validation error.
        form = SecuredropPageForm(
            directory_page=self.directory,
            data={
                'title': self.securedrop_page.title,
                'landing_page_domain': self.securedrop_page.landing_page_domain + 'm',
                'onion_address': self.securedrop_page.onion_address + 'm.onion',
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            },
            instance=self.securedrop_page,
        )

        self.assertTrue(form.is_valid())

    def test_validate_unique_title__valid__different_instance(self):
        # A form without a duplicate title should validate fine.
        form = SecuredropPageForm(
            directory_page=self.directory,
            data={
                'title': self.securedrop_page.title + 'm',
                'landing_page_domain': self.securedrop_page.landing_page_domain + 'm',
                'onion_address': self.securedrop_page.onion_address + 'm.onion',
                'languages': 'null',
                'topics': 'null',
                'countries': 'null',
            },
        )

        self.assertTrue(form.is_valid())
