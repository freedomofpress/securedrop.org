from django.core.handlers.wsgi import WSGIHandler
from django.test import TestCase

from securedrop import wsgi


class WSGISmokeTest(TestCase):
    def test_smoke_wsgi(self):
        self.assertTrue(isinstance(wsgi.application, WSGIHandler))
