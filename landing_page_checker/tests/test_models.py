from django.core.exceptions import ValidationError
from django.test import TestCase

from landing_page_checker.models import SecuredropPage, Result
from landing_page_checker.tests.factories import SecuredropPageFactory, ResultFactory


class SecuredropPageTest(TestCase):
    def test_securedrop_can_save_expected_urls(self):
        securedrop = SecuredropPageFactory(
            landing_page_domain='https://www.something.org',
            onion_address='https://notreal.onion',
        )
        securedrop.save()
        self.assertIn(securedrop, SecuredropPage.objects.all())

    def test_securedrop_cannot_save_invalid_url(self):
        with self.assertRaises(ValidationError):
            SecuredropPageFactory(
                landing_page_domain='something',
            )

    def test_securedrop_cannot_save_invalid_onion_address(self):
        with self.assertRaises(ValidationError):
            SecuredropPageFactory(
                onion_address='https://notreal.com',
            )

    def test_securedrop_cannot_save_empty_urls(self):
        with self.assertRaises(ValidationError):
            SecuredropPageFactory(
                landing_page_domain='',
            )

    def test_duplicate_landing_pages_are_invalid(self):
        landing_page_domain = 'https://www.freedom.press'

        SecuredropPageFactory(
            landing_page_domain=landing_page_domain,
        )
        with self.assertRaises(ValidationError):
            SecuredropPageFactory(
                landing_page_domain=landing_page_domain,
            )

    def test_duplicate_onion_addresses_are_invalid(self):
        onion_address = 'https://notreal.onion'

        SecuredropPageFactory(
            onion_address=onion_address,
        )
        with self.assertRaises(ValidationError):
            SecuredropPageFactory(
                onion_address=onion_address,
            )

    def test_securedrop_string_representation(self):
        securedrop1 = SecuredropPageFactory(
            title='Freedom of the Press Foundation',
        )
        self.assertIn(securedrop1.title, securedrop1.__str__())

    def test_returns_latest_live_result(self):
        sd = SecuredropPageFactory()
        ResultFactory(live=False, securedrop=sd, landing_page_domain=sd.landing_page_domain).save()
        ResultFactory(live=False, securedrop=sd, landing_page_domain=sd.landing_page_domain).save()
        r3 = ResultFactory(live=True, securedrop=sd, landing_page_domain=sd.landing_page_domain)
        r3.save()

        sd = SecuredropPage.objects.get(pk=sd.pk)

        self.assertEqual(r3, sd.get_live_result())

    def test_save_associates_results(self):
        landing_page_domain = 'https://www.something.org'
        result = Result(
            live=True,
            hsts=True,
            hsts_max_age=True,
            securedrop=None,
            landing_page_domain=landing_page_domain,
        )
        result.save()

        securedrop = SecuredropPageFactory(
            landing_page_domain=landing_page_domain,
            onion_address='https://notreal.onion',
        )
        securedrop.save()
        result.refresh_from_db()
        self.assertEqual(result.securedrop, securedrop)


class ResultTest(TestCase):
    def setUp(self):
        self.securedrop = SecuredropPageFactory()
        self.securedrop.save()

    def test_grade_computed_on_save(self):
        result = Result(live=True, hsts=True, hsts_max_age=True,
                        securedrop=self.securedrop)
        self.assertEqual(result.grade, '?')
        result.save()
        self.assertEqual(result.grade, 'A')

    def test_an_instance_using_cookies_gets_an_F(self):
        result = Result(live=True, no_cookies=False, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'F')

    def test_an_instance_using_a_cdn_gets_a_D(self):
        result = Result(live=True, no_cdn=False, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'D')

    def test_an_instance_using_a_subdomain_gets_a_D(self):
        result = Result(live=True, subdomain=True, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'D')

    def test_an_instance_showing_server_software_in_headers_gets_a_D(self):
        result = Result(live=True, no_server_info=False,
                        securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'D')

    def test_an_instance_showing_server_version_in_headers_gets_a_D(self):
        result = Result(live=True, no_server_version=False,
                        securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'D')

    def test_an_instance_with_expires_not_set_gets_a_C(self):
        result = Result(live=True, expires_set=False,
                        securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'C')

    def test_an_instance_with_cache_control_nostore_not_set_gets_a_B(self):
        result = Result(live=True, cache_control_nostore_set=False,
                        hsts_max_age=True, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'B')

    def test_a_down_instance_gets_a_null_grade(self):
        result = Result(live=False, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, '?')

    def test_securedrop_can_get_most_recent_scan(self):
        result1 = Result(live=True, hsts=True, hsts_max_age=True,
                         securedrop=self.securedrop, landing_page_domain=self.securedrop.landing_page_domain)
        result1.save()
        result2 = Result(live=True, hsts=False, hsts_max_age=True,
                         securedrop=self.securedrop, landing_page_domain=self.securedrop.landing_page_domain)
        result2.save()
        securedrop = SecuredropPage.objects.get(id=self.securedrop.pk)
        most_recent = securedrop.results.latest()
        self.assertEqual(most_recent.grade, 'C')

    def test_result_string_representation(self):
        result1 = Result(live=True, hsts=True, hsts_max_age=True,
                         securedrop=self.securedrop, landing_page_domain=self.securedrop.landing_page_domain)
        self.assertIn(result1.landing_page_domain, result1.__str__())

    def test_is_equal_to_compares_only_scan_attributes__same_result(self):
        """Test is_equal_to does not compare pk, _state, etc."""
        result1 = Result(live=True, hsts=True, hsts_max_age=True,
                         securedrop=self.securedrop)
        result2 = Result(live=True, hsts=True, hsts_max_age=True,
                         securedrop=self.securedrop)
        self.assertTrue(result1.is_equal_to(result2))

    def test_is_equal_to_compares_only_scan_attributes__new_result(self):
        result1 = Result(live=True, hsts=True, hsts_max_age=True, securedrop=self.securedrop)
        result2 = Result(live=False, securedrop=self.securedrop)
        self.assertFalse(result1.is_equal_to(result2))

    def test_save_associates_results(self):
        result = Result(
            live=True,
            hsts=True,
            hsts_max_age=True,
            securedrop=None,
            landing_page_domain=self.securedrop.landing_page_domain,
        )
        result.save()
        self.assertEqual(result.securedrop, self.securedrop)
