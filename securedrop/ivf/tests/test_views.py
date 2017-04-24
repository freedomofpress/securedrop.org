from django.test import TestCase
from django.utils.html import escape

from ivf.forms import LandingPageForm
from ivf.views import home_page


class HomePageTest(TestCase):
    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_includes_landing_page_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], LandingPageForm)

    def post_invalid_input(self):
        return self.client.post(
            '/',
            data = {'url': ''}
        )

    def test_invalid_input_returns_home(self):
        response = self.post_invalid_input()
        self.assertTemplateUsed(response, 'home.html')
