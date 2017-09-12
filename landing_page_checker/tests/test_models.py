from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.test import TestCase

from landing_page_checker.models import Securedrop, Result


class SecuredropTest(TestCase):
    def test_securedrop_can_save_expected_urls(self):
        securedrop = Securedrop(organization='Freedom of the Press Foundation',
                                landing_page_domain='freedom.press',
                                onion_address='notreal.onion')
        securedrop.save()
        self.assertIn(securedrop, Securedrop.objects.all())

    def test_securedrop_cannot_save_empty_urls(self):
        securedrop = Securedrop()
        with self.assertRaises(ValidationError):
            securedrop.save()
            securedrop.full_clean()

    def test_duplicate_securedrops_are_invalid(self):
        securedrop1 = Securedrop(organization='Freedom of the Press Foundation',
                                 landing_page_domain='freedom.press',
                                 onion_address='notreal.onion')
        securedrop1.save()
        securedrop2 = Securedrop(organization='Freedom of the Press Foundation',
                                 landing_page_domain='freedom.press',
                                 onion_address='notreal.onion')
        with self.assertRaises(IntegrityError):
            securedrop2.save()

    def test_securedrop_string_representation(self):
        securedrop1 = Securedrop(organization='Freedom of the Press Foundation',
                                 landing_page_domain='freedom.press',
                                 onion_address='notreal.onion')
        self.assertIn(securedrop1.organization, securedrop1.__str__())


class ResultTest(TestCase):
    def setUp(self):
        self.securedrop = Securedrop.objects.create(
            organization='Freedom of the Press Foundation',
            landing_page_domain='freedom.press',
            onion_address='notreal.onion'
        )

    def test_grade_computed_on_save(self):
        result = Result(live=True, hsts=True, hsts_max_age=99999999,
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
                        hsts_max_age=99999999, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'B')

    def test_a_down_instance_gets_a_null_grade(self):
        result = Result(live=False, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, '?')

    def test_securedrop_can_get_most_recent_scan(self):
        result1 = Result(live=True, hsts=True, hsts_max_age=99999999,
                         securedrop=self.securedrop)
        result1.save()
        result2 = Result(live=True, hsts=False, hsts_max_age=99999999,
                         securedrop=self.securedrop)
        result2.save()
        most_recent = self.securedrop.results.latest()
        self.assertEqual(most_recent.grade, 'C')

    def test_result_string_representation(self):
        result1 = Result(live=True, hsts=True, hsts_max_age=99999999,
                         securedrop=self.securedrop)
        self.assertIn(result1.securedrop.organization, result1.__str__())

    def test_custom_eq_operator_compares_only_scan_attributes__same_result(self):
        """Test custom __eq__ does not compare pk, _state, etc."""
        result1 = Result(live=True, hsts=True, hsts_max_age=99999999,
                         securedrop=self.securedrop)
        result2 = Result(live=True, hsts=True, hsts_max_age=99999999,
                         securedrop=self.securedrop)
        self.assertTrue(result1 == result2)

    def test_custom_eq_operator_compares_only_scan_attributes__new_result(self):
        result1 = Result(live=True, hsts=True, hsts_max_age=99999999,
                         securedrop=self.securedrop)
        result2 = Result(live=False, securedrop=self.securedrop)
        self.assertFalse(result1 == result2)
