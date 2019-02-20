from allauth.account.models import EmailAddress

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from wagtail.core.models import Site

from directory.warnings import WarningLevel
from directory.models import DirectoryEntry, ScanResult, SecuredropOwner
from directory.tests.factories import DirectoryEntryFactory, ScanResultFactory, DirectoryPageFactory


class DirectoryEntryTest(TestCase):
    def test_securedrop_can_save_expected_urls(self):
        securedrop = DirectoryEntryFactory(
            landing_page_url='https://www.something.org',
            onion_address='https://notreal.onion',
        )
        securedrop.save()
        self.assertIn(securedrop, DirectoryEntry.objects.all())

    def test_securedrop_cannot_save_invalid_url(self):
        with self.assertRaises(ValidationError):
            DirectoryEntryFactory(
                landing_page_url='something',
            )

    def test_securedrop_cannot_save_invalid_onion_address(self):
        with self.assertRaises(ValidationError):
            DirectoryEntryFactory(
                onion_address='https://notreal.com',
            )

    def test_securedrop_cannot_save_empty_urls(self):
        with self.assertRaises(ValidationError):
            DirectoryEntryFactory(
                landing_page_url='',
            )

    def test_duplicate_landing_pages_are_invalid(self):
        landing_page_url = 'https://www.freedom.press'

        DirectoryEntryFactory(
            landing_page_url=landing_page_url,
        )
        with self.assertRaises(ValidationError):
            DirectoryEntryFactory(
                landing_page_url=landing_page_url,
            )

    def test_securedrop_string_representation(self):
        securedrop1 = DirectoryEntryFactory(
            title='Freedom of the Press Foundation',
        )
        self.assertIn(securedrop1.title, securedrop1.__str__())

    def test_returns_latest_live_result(self):
        sd = DirectoryEntryFactory()
        ScanResultFactory(live=False, securedrop=sd, landing_page_url=sd.landing_page_url).save()
        ScanResultFactory(live=False, securedrop=sd, landing_page_url=sd.landing_page_url).save()
        r3 = ScanResultFactory(live=True, securedrop=sd, landing_page_url=sd.landing_page_url)
        r3.save()

        sd = DirectoryEntry.objects.get(pk=sd.pk)

        self.assertEqual(r3, sd.get_live_result())

    def test_save_associates_results(self):
        landing_page_url = 'https://www.something.org'
        result = ScanResult(
            live=True,
            hsts=True,
            hsts_max_age=True,
            securedrop=None,
            landing_page_url=landing_page_url,
        )
        result.save()

        securedrop = DirectoryEntryFactory(
            landing_page_url=landing_page_url,
            onion_address='https://notreal.onion',
        )
        securedrop.save()
        result.refresh_from_db()
        self.assertEqual(result.securedrop, securedrop)


class ScanResultTest(TestCase):
    def setUp(self):
        self.securedrop = DirectoryEntryFactory()
        self.securedrop.save()

    def test_instance_on_subdomain_gets_moderate_warning(self):
        result = ScanResultFactory(no_failures=True, subdomain=True)
        self.assertEqual(self.securedrop.get_warnings(result)[0].level, WarningLevel.MODERATE)

    def test_instance_with_incorrect_referrer_policy_gets_moderate_warning(self):
        result = ScanResultFactory(no_failures=True, referrer_policy_set_to_no_referrer=False)
        self.assertEqual(self.securedrop.get_warnings(result)[0].level, WarningLevel.MODERATE)

    def test_instance_with_unsafe_onion_addresses_gets_moderate_warning(self):
        result = ScanResultFactory(no_failures=True, safe_onion_address=False)
        self.assertEqual(self.securedrop.get_warnings(result)[0].level, WarningLevel.MODERATE)

    def test_instance_with_third_party_cookies_gets_no_warning(self):
        result = ScanResultFactory(no_failures=True, no_cookies=False)
        self.assertEqual(self.securedrop.get_warnings(result), [])

    def test_instance_with_analytics_gets_severe_warning(self):
        result = ScanResultFactory(no_failures=True, no_analytics=False)
        self.assertEqual(self.securedrop.get_warnings(result)[0].level, WarningLevel.SEVERE)

    def test_instance_with_cdn_gets_no_warning(self):
        result = ScanResultFactory(no_failures=True, no_cdn=False)

        self.assertEqual(self.securedrop.get_warnings(result), [])

    def test_instance_with_cross_domain_assets_gets_severe_warning(self):
        result = ScanResultFactory(no_failures=True, no_cross_domain_assets=False)
        self.assertEqual(self.securedrop.get_warnings(result)[0].level, WarningLevel.SEVERE)

    def test_grade_computed_on_save(self):
        result = ScanResult(live=True, hsts=True, hsts_max_age=True,
                            securedrop=self.securedrop)
        self.assertEqual(result.grade, '?')
        result.save()
        self.assertEqual(result.grade, 'A')

    def test_an_instance_using_cookies_gets_an_F(self):
        result = ScanResult(live=True, no_cookies=False, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'F')

    def test_an_instance_using_a_cdn_gets_a_D(self):
        result = ScanResult(live=True, no_cdn=False, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'D')

    def test_an_instance_using_a_subdomain_gets_a_D(self):
        result = ScanResult(live=True, subdomain=True, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'D')

    def test_an_instance_showing_server_software_in_headers_gets_a_D(self):
        result = ScanResult(live=True, no_server_info=False,
                            securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'D')

    def test_an_instance_showing_server_version_in_headers_gets_a_D(self):
        result = ScanResult(live=True, no_server_version=False,
                            securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'D')

    def test_an_instance_with_expires_not_set_gets_a_C(self):
        result = ScanResult(live=True, expires_set=False,
                            securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'C')

    def test_an_instance_with_cache_control_nostore_not_set_gets_a_B(self):
        result = ScanResult(live=True, cache_control_nostore_set=False,
                            hsts_max_age=True, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, 'B')

    def test_a_down_instance_gets_a_null_grade(self):
        result = ScanResult(live=False, securedrop=self.securedrop)
        result.save()
        self.assertEqual(result.grade, '?')

    def test_securedrop_can_get_most_recent_scan(self):
        result1 = ScanResult(live=True, hsts=True, hsts_max_age=True,
                             securedrop=self.securedrop, landing_page_url=self.securedrop.landing_page_url)
        result1.save()
        result2 = ScanResult(live=True, hsts=False, hsts_max_age=True,
                             securedrop=self.securedrop, landing_page_url=self.securedrop.landing_page_url)
        result2.save()
        securedrop = DirectoryEntry.objects.get(id=self.securedrop.pk)
        most_recent = securedrop.results.latest()
        self.assertEqual(most_recent.grade, 'C')

    def test_result_string_representation(self):
        result1 = ScanResult(live=True, hsts=True, hsts_max_age=True,
                             securedrop=self.securedrop, landing_page_url=self.securedrop.landing_page_url)
        self.assertIn(result1.landing_page_url, result1.__str__())

    def test_is_equal_to_compares_only_scan_attributes__same_result(self):
        """Test is_equal_to does not compare pk, _state, etc."""
        result1 = ScanResult(live=True, hsts=True, hsts_max_age=True,
                             securedrop=self.securedrop)
        result2 = ScanResult(live=True, hsts=True, hsts_max_age=True,
                             securedrop=self.securedrop)
        self.assertTrue(result1.is_equal_to(result2))

    def test_is_equal_to_compares_only_scan_attributes__new_result(self):
        result1 = ScanResult(live=True, hsts=True, hsts_max_age=True, securedrop=self.securedrop)
        result2 = ScanResult(live=False, securedrop=self.securedrop)
        self.assertFalse(result1.is_equal_to(result2))

    def test_save_associates_results(self):
        result = ScanResult(
            live=True,
            hsts=True,
            hsts_max_age=True,
            securedrop=None,
            landing_page_url=self.securedrop.landing_page_url,
        )
        result.save()
        self.assertEqual(result.securedrop, self.securedrop)


class SecuredropQuerySetTestCase(TestCase):
    def test_domain_annotation(self):
        DirectoryEntryFactory.create(
            landing_page_url="https://securedrop.org/subpath"
        )
        securedrop_page_qs = DirectoryEntry.objects.with_domain_annotation()

        self.assertEqual(
            securedrop_page_qs.values_list('domain', flat=True)[0],
            'securedrop.org'
        )

    def test_listed(self):
        """
        QuerySet method `listed` should return only listed DirectoryEntries
        """
        DirectoryEntryFactory.create(delisted='other')
        DirectoryEntryFactory.create(delisted='other')
        l1 = DirectoryEntryFactory.create()
        l2 = DirectoryEntryFactory.create()
        self.assertCountEqual(
            DirectoryEntry.objects.listed(),
            [l1, l2]
        )

    def test_delisted(self):
        """
        QuerySet method `delisted` should return only delisted DirectoryEntries
        """
        d1 = DirectoryEntryFactory.create(delisted='other')
        d2 = DirectoryEntryFactory.create(delisted='other')
        DirectoryEntryFactory.create()
        DirectoryEntryFactory.create()
        self.assertCountEqual(
            DirectoryEntry.objects.delisted(),
            [d1, d2]
        )


class DirectoryEntrySearchTest(TestCase):
    def setUp(self):
        self.title = 'Awesome'
        self.landing_page_url = 'https://landing.com'
        self.onion_address = 'something.onion'
        self.description = 'Amaze'
        self.sd = DirectoryEntryFactory(
            title=self.title,
            landing_page_url=self.landing_page_url,
            onion_address=self.onion_address,
            organization_description=self.description
        )
        self.search_content = self.sd.get_search_content()

    def test_get_search_content_indexes_title(self):
        self.assertIn(self.title, self.search_content.text)

    def test_get_search_content_indexes_landing_page_url(self):
        self.assertIn(self.landing_page_url, self.search_content.text)

    def test_get_search_content_indexes_onion_address(self):
        self.assertIn(self.onion_address, self.search_content.text)

    def test_get_search_content_indexes_description(self):
        self.assertIn(self.onion_address, self.search_content.text)

    def test_get_search_content_indexes_languages(self):
        language = self.sd.languages.first().title
        self.assertIn(language, self.search_content.text)

    def test_get_search_content_indexes_topics(self):
        topic = self.sd.topics.first().title
        self.assertIn(topic, self.search_content.text)

    def test_get_search_content_indexes_countries(self):
        country = self.sd.countries.first().title
        self.assertIn(country, self.search_content.text)


class DirectoryEntryAuthTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = Client()
        self.username = "Rachel"
        self.email = "r@r.com"
        self.password = "rachel"
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password, is_active=True)
        self.user.save()
        # Create a verified email address object for this user via allauth
        EmailAddress.objects.create(user=self.user, email=self.email, verified=True)
        # Setup pages. Site is needed for valid urls.
        site = Site.objects.get()
        directory = DirectoryPageFactory(parent=site.root_page)
        self.unowned_sd_page = DirectoryEntryFactory(live=True, parent=directory)
        self.unowned_sd_page.save()
        self.user_owned_sd_page = DirectoryEntryFactory(live=True, parent=directory)
        self.user_owned_sd_page.save()
        SecuredropOwner(owner=self.user, page=self.user_owned_sd_page).save()

    def test_logged_in_user_should_see_edit_on_owned_pages(self):
        # Login
        self.client.post(reverse_lazy('account_login'), {'login': self.email, 'password': self.password})
        response = self.client.get(self.user_owned_sd_page.url)
        self.assertTrue(response.context['page'].editable)

    def test_logged_out_user_should_not_see_edit(self):
        response = self.client.get(self.user_owned_sd_page.url)
        self.assertFalse(response.context['page'].editable)

    def test_logged_in_user_should_not_see_edit_on_unowned_pages(self):
        self.client.post(reverse_lazy('account_login'), {'login': self.email, 'password': self.password})
        response = self.client.get(self.unowned_sd_page.url)
        self.assertFalse(response.context['page'].editable)
