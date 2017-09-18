from django.test import TestCase

from landing_page_checker.forms import LandingPageForm


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
