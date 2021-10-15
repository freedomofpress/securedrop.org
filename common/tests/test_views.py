from django.test import TestCase


class HealthCheckTestCase(TestCase):
    def test_health_check_url_returns_200_status(self):
        self.response = self.client.get("/health/ok/")
        self.assertEqual(self.response.status_code, 200)

    def test_version_info_url_returns_200_status(self):
        self.response = self.client.get("/health/version/")
        self.assertEqual(self.response.status_code, 200)
