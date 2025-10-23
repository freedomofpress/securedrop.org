from django.test import TestCase
from django.urls import reverse


class HealthCheckTestCase(TestCase):
    def test_health_check_url_returns_200_status(self):
        self.response = self.client.get("/health/ok/")
        self.assertEqual(self.response.status_code, 200)

    def test_version_info_url_returns_200_status(self):
        self.response = self.client.get("/health/version/")
        self.assertEqual(self.response.status_code, 200)


class TooManyRequestsTestCase(TestCase):
    def test_too_many_requests_uses_correct_template(self):
        with self.assertTemplateUsed("429.html"):
            self.response = self.client.get(reverse('too_many_requests'))
