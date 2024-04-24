from django.test import TestCase
from django.test.client import RequestFactory
from wagtail.models import Site

from directory.tests.factories import (
    DirectoryPageFactory,
    LanguageFactory,
    CountryFactory,
    TopicFactory,
    DirectoryEntryFactory,
)


class DirectoryFilterTest(TestCase):
    def setUp(self):
        self.directory = DirectoryPageFactory()
        self.child = DirectoryEntryFactory(parent=self.directory)
        self.not_child = DirectoryEntryFactory(parent=None)

    def test_directory_returns_its_children(self):
        filtered_instances = self.directory.get_instances()
        self.assertIn(self.child, filtered_instances)

    def test_directory_does_not_return_instances_that_are_not_children(self):
        filtered_instances = self.directory.get_instances()
        self.assertNotIn(self.not_child, filtered_instances)


class DirectoryPageContextTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.directory = DirectoryPageFactory(parent=site.root_page)

    def setUp(self):
        self.factory = RequestFactory()

    def test_correct_search_term_returned_in_context(self):
        search_term = "Amet"
        request = self.factory.get(self.directory.url, {
            'search': search_term,
        })
        context = self.directory.get_context(request)
        self.assertEqual(
            context['entries_filters'],
            {'title__icontains': search_term},
        )
        self.assertEqual(context['search_value'], search_term)

    def test_correct_language_returned_in_context(self):
        georgian = LanguageFactory(title="Georgian")

        request = self.factory.get(self.directory.url, {
            'language': str(georgian.pk),
        })
        context = self.directory.get_context(request)
        self.assertEqual(context['entries_filters'], {'languages': georgian})

    def test_correct_country_returned_in_context(self):
        honduras = CountryFactory(title="Honduras")
        request = self.factory.get(self.directory.url, {
            'country': str(honduras.pk),
        })
        context = self.directory.get_context(request)
        self.assertEqual(context['entries_filters'], {'countries': honduras})

    def test_correct_topic_returned_from_querydict(self):
        sports = TopicFactory(title="sports")
        request = self.factory.get(self.directory.url, {
            'topic': str(sports.pk),
        })
        context = self.directory.get_context(request)
        self.assertEqual(context['entries_filters'], {'topics': sports})

    def test_non_int_id_does_not_break_filters(self):
        request = self.factory.get(self.directory.url, {
            'topic': 'foo',
        })
        context = self.directory.get_context(request)
        self.assertEqual(context['entries_filters'], {})

    def test_invalid_topic_id_does_not_break_filters(self):
        request = self.factory.get(self.directory.url, {
            'topic': '1000000',
        })
        context = self.directory.get_context(request)
        self.assertEqual(context['entries_filters'], {})

    def test_invalid_language_id_does_not_break_filters(self):
        request = self.factory.get(self.directory.url, {
            'language': '1000000',
        })
        context = self.directory.get_context(request)
        self.assertEqual(context['entries_filters'], {})

    def test_multiple_filters_returned_from_querydict(self):
        search_term = "Amet"
        afrikaans = LanguageFactory(title="Afrikaans")
        thailand = CountryFactory(title="Country")
        scotus = TopicFactory(title="SCOTUS")

        request = self.factory.get(self.directory.url, {
            'search': search_term,
            'language': str(afrikaans.pk),
            'country': str(thailand.pk),
            'topic': str(scotus.pk),
        })
        context = self.directory.get_context(request)
        self.assertEqual(
            context['entries_filters'],
            {
                'title__icontains': search_term,
                'languages': afrikaans,
                'countries': thailand,
                'topics': scotus,
            },
        )


class DirectoryLanguageFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.directory = DirectoryPageFactory(parent=site.root_page)

        spanish = LanguageFactory(title='Spanish')
        chinese = LanguageFactory(title='Chinese')
        # set up instances that are children of the directory and have those languages
        cls.spanish_instance = DirectoryEntryFactory(languages=0, parent=cls.directory)
        cls.spanish_instance.languages.add(spanish)
        cls.spanish_instance.save()

        cls.chinese_instance = DirectoryEntryFactory(languages=0, parent=cls.directory)
        cls.chinese_instance.languages.add(chinese)
        cls.chinese_instance.save()
        cls.lang_filter = {'languages': spanish}
        cls.spanish = spanish

    def test_language_filtered_for_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.lang_filter)
        self.assertIn(self.spanish_instance, filtered_instances)

    def test_language_not_filtered_for_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.lang_filter)
        self.assertNotIn(self.chinese_instance, filtered_instances)

    def test_filters_based_on_get_parameters(self):
        response = self.client.get(self.directory.url, {
            'language': str(self.spanish.pk)
        })
        self.assertEqual(
            response.context['entries_page'].object_list,
            [self.spanish_instance],
        )


class DirectoryCountryFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.directory = DirectoryPageFactory(parent=site.root_page)

        cls.mexico = CountryFactory(title='Mexico')
        cls.azerbaijan = CountryFactory(title='Azerbaijan')

        # set up instances that are children of the directory and have those countries
        cls.mexico_instance = DirectoryEntryFactory(
            parent=cls.directory,
            countries=0,
        )
        cls.mexico_instance.countries.add(cls.mexico)
        cls.mexico_instance.save()

        cls.azerbaijan_instance = DirectoryEntryFactory(
            parent=cls.directory,
            countries=0,
        )
        cls.azerbaijan_instance.countries.add(cls.azerbaijan)
        cls.azerbaijan_instance.save()
        cls.country_filter = {'countries': cls.mexico}

    def test_country_filtered_for_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.country_filter)
        self.assertIn(self.mexico_instance, filtered_instances)

    def test_country_not_filtered_for_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.country_filter)
        self.assertNotIn(self.azerbaijan_instance, filtered_instances)

    def test_filters_based_on_get_parameters(self):
        response = self.client.get(self.directory.url, {
            'country': str(self.mexico.pk)
        })
        self.assertEqual(
            response.context['entries_page'].object_list,
            [self.mexico_instance],
        )


class DirectoryTopicFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.directory = DirectoryPageFactory(parent=site.root_page)

        cls.pf = TopicFactory(title='Press Freedom')
        cls.irs = TopicFactory(title='IRS')

        # set up instances that are children of the directory and have those topics
        cls.pf_instance = DirectoryEntryFactory(parent=cls.directory)
        cls.pf_instance.topics.add(cls.pf)
        cls.pf_instance.save()

        cls.irs_instance = DirectoryEntryFactory(parent=cls.directory)
        cls.irs_instance.topics.add(cls.irs)
        cls.irs_instance.save()
        cls.topic_filter = {'topics': cls.pf}

    def test_topic_filtered_for_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.topic_filter)
        self.assertIn(self.pf_instance, filtered_instances)

    def test_topic_not_filtered_for_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.topic_filter)
        self.assertNotIn(self.irs_instance, filtered_instances)

    def test_filters_based_on_get_parameters(self):
        response = self.client.get(self.directory.url, {
            'topic': str(self.pf.pk)
        })
        self.assertEqual(
            response.context['entries_page'].object_list,
            [self.pf_instance],
        )


class DirectorySearchFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.directory = DirectoryPageFactory(parent=site.root_page)
        cls.best_instance = DirectoryEntryFactory(
            title="Best Instance",
            parent=cls.directory
        )
        cls.worst_instance = DirectoryEntryFactory(
            title="Worst Instance",
            parent=cls.directory
        )
        cls.search_filter = {'title__icontains': 'best'}

    def test_title_searched_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.search_filter)
        self.assertIn(self.best_instance, filtered_instances)

    def test_title_not_searched_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.search_filter)
        self.assertNotIn(self.worst_instance, filtered_instances)

    def test_filters_based_on_get_parameters(self):
        response = self.client.get(self.directory.url, {
            'search': 'best',
        })
        self.assertEqual(
            response.context['entries_page'].object_list,
            [self.best_instance],
        )

    def test_does_not_search_if_query_includes_null_characters(self):
        response = self.client.get(self.directory.url, {
            'search': 'be\x00st',
        })
        self.assertEqual(response.status_code, 200)


class DirectoryMultipleFiltersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.directory = DirectoryPageFactory(parent=site.root_page)

        cls.spanish = LanguageFactory(title='Spanish')
        cls.chinese = LanguageFactory(title='Chinese')

        cls.mexico = CountryFactory(title='Mexico')
        cls.azerbaijan = CountryFactory(title='Azerbaijan')

        cls.pf = TopicFactory(title='Press Freedom')
        cls.irs = TopicFactory(title='IRS')

        # set up instances that are children of the directory and have multiple categories
        cls.sp_mx_instance = DirectoryEntryFactory(parent=cls.directory)
        cls.sp_mx_instance.languages.add(cls.spanish)
        cls.sp_mx_instance.countries.add(cls.mexico)
        cls.sp_mx_instance.save()

        cls.az_pf_instance = DirectoryEntryFactory(parent=cls.directory)
        cls.az_pf_instance.countries.add(cls.azerbaijan)
        cls.az_pf_instance.topics.add(cls.pf)
        cls.az_pf_instance.save()

        cls.other_instance = DirectoryEntryFactory(
            parent=cls.directory,
            languages=0,
            countries=0,
        )
        cls.other_instance.languages.add(cls.spanish)
        cls.other_instance.topics.add(cls.pf)
        cls.other_instance.save()

        cls.lang_country_filter = {
            'languages': cls.spanish,
            'countries': cls.mexico,
        }

        cls.country_topic_filter = {
            'countries': cls.azerbaijan,
            'topics': cls.pf,
        }

    def test_country_and_language_filter(self):
        filtered_instances = self.directory.get_instances(filters=self.lang_country_filter)
        self.assertIn(self.sp_mx_instance, filtered_instances)
        self.assertNotIn(self.other_instance, filtered_instances)

    def test_country_and_language_filtered_based_on_get_parameters(self):
        response = self.client.get(self.directory.url, {
            'language': str(self.spanish.pk),
            'country': str(self.mexico.pk),
        })
        self.assertEqual(
            response.context['entries_page'].object_list,
            [self.sp_mx_instance],
        )

    def test_country_and_topic_filter(self):
        filtered_instances = self.directory.get_instances(filters=self.country_topic_filter)
        self.assertIn(self.az_pf_instance, filtered_instances)
        self.assertNotIn(self.other_instance, filtered_instances)

    def test_country_and_topic_filtered_based_on_get_parameters(self):
        response = self.client.get(self.directory.url, {
            'topic': str(self.pf.pk),
            'country': str(self.azerbaijan.pk),
        })
        self.assertEqual(
            response.context['entries_page'].object_list,
            [self.az_pf_instance],
        )
