from django.test import TestCase

from directory.forms import LandingPageForm


class HomePageTest(TestCase):
    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class SecuredropDirectoryTest(TestCase):
    def test_securedrop_directory_renders_home_template(self):
        response = self.client.get('/directory', follow=True)
        self.assertTemplateUsed(response, 'home.html')


class LandingPageScannerTest(TestCase):
    def landing_page_scanner_renders_correct_template(self):
        response = self.client.get('/test')
        self.assertTemplateUsed(response, 'landing_page_test.html')

    def test_landing_page_scanner_includes_landing_page_form(self):
        response = self.client.get('/test', follow=True)
        self.assertIsInstance(response.context['form'], LandingPageForm)

    def test_invalid_input_returns_to_landing_page_scanner(self):
        response = self.client.post(
            '/test',
            data={'url': ''},
            follow=True
        )
        self.assertTemplateUsed(response, 'landing_page_test.html')
