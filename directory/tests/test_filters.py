from django.test import TestCase
from django.http import QueryDict

from directory.tests.factories import (
    DirectoryPageFactory,
    LanguageFactory,
    CountryFactory,
    TopicFactory,
    SecuredropPageFactory,
)


class DirectoryFilterTest(TestCase):
    def setUp(self):
        self.directory = DirectoryPageFactory()
        self.child = SecuredropPageFactory(parent=self.directory)
        self.not_child = SecuredropPageFactory(parent=None)

    def test_directory_returns_its_children(self):
        filtered_instances = self.directory.get_instances()
        self.assertIn(self.child, filtered_instances)

    def test_directory_does_not_return_instances_that_are_not_children(self):
        filtered_instances = self.directory.get_instances()
        self.assertNotIn(self.not_child, filtered_instances)


class FiltersFromQueryDictTest(TestCase):
    def setUp(self):
        self.directory = DirectoryPageFactory()

    def test_correct_search_term_returned_from_querydict(self):
        search_term = "Amet"
        querydict = QueryDict('search={}'.format(search_term))
        filters = self.directory.filters_from_querydict(querydict)
        self.assertEqual(filters['title__icontains'], search_term)

    def test_correct_language_returned_from_querydict(self):
        georgian = LanguageFactory(title="Georgian")
        georgian.save()
        querydict = QueryDict('language={}'.format(georgian.id))
        filters = self.directory.filters_from_querydict(querydict)
        self.assertEqual(filters['languages'], georgian)

    def test_correct_country_returned_from_querydict(self):
        honduras = CountryFactory(title="Honduras")
        honduras.save()
        querydict = QueryDict('country={}'.format(honduras.id))
        filters = self.directory.filters_from_querydict(querydict)
        self.assertEqual(filters['countries'], honduras)

    def test_correct_topic_returned_from_querydict(self):
        sports = TopicFactory(title="sports")
        sports.save()
        querydict = QueryDict('topic={}'.format(sports.id))
        filters = self.directory.filters_from_querydict(querydict)
        self.assertEqual(filters['topics'], sports)

    def test_non_int_id_does_not_break_filters(self):
        querydict = QueryDict('topic=foo')
        filters = self.directory.filters_from_querydict(querydict)
        self.assertEqual({}, filters)

    def test_invalid_id_does_not_break_filters(self):
        querydict = QueryDict('language=100000')
        filters = self.directory.filters_from_querydict(querydict)
        self.assertEqual({}, filters)

    def test_multiple_filters_returned_from_querydict(self):
        search_term = "Amet"
        afrikaans = LanguageFactory(title="Afrikaans")
        afrikaans.save()
        thailand = CountryFactory(title="Country")
        thailand.save()
        scotus = TopicFactory(title="SCOTUS")
        scotus.save()
        querydict = QueryDict('search={}&language={}&topic={}&country={}'.format(
            search_term,
            afrikaans.id,
            scotus.id,
            thailand.id
        ))
        filters = self.directory.filters_from_querydict(querydict)
        self.assertEqual(filters['title__icontains'], search_term)
        self.assertEqual(filters['topics'], scotus)
        self.assertEqual(filters['countries'], thailand)
        self.assertEqual(filters['languages'], afrikaans)


class DirectoryLanguageFilterTest(TestCase):
    def setUp(self):
        self.directory = DirectoryPageFactory()
        # set up languages
        spanish = LanguageFactory(title='Spanish')
        chinese = LanguageFactory(title='Chinese')
        spanish.save()
        chinese.save()
        # set up instances that are children of the directory and have those languages
        self.spanish_instance = SecuredropPageFactory(parent=self.directory)
        self.spanish_instance.languages.add(spanish)
        self.spanish_instance.save()

        self.chinese_instance = SecuredropPageFactory(parent=self.directory)
        self.chinese_instance.languages.add(chinese)
        self.chinese_instance.save()
        self.lang_filter = {'languages': spanish}

    def test_language_filtered_for_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.lang_filter)
        self.assertIn(self.spanish_instance, filtered_instances)

    def test_langauge_not_filtered_for_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.lang_filter)
        self.assertNotIn(self.chinese_instance, filtered_instances)


class DirectoryCountryFilterTest(TestCase):
    def setUp(self):
        self.directory = DirectoryPageFactory()
        # set up countries
        mexico = CountryFactory(title='Mexico')
        azerbaijan = CountryFactory(title='Azerbaijan')
        mexico.save()
        azerbaijan.save()
        # set up instances that are children of the directory and have those countries
        self.mexico_instance = SecuredropPageFactory(parent=self.directory)
        self.mexico_instance.countries.add(mexico)
        self.mexico_instance.save()

        self.azerbaijan_instance = SecuredropPageFactory(parent=self.directory)
        self.azerbaijan_instance.countries.add(azerbaijan)
        self.azerbaijan_instance.save()
        self.country_filter = {'countries': mexico}

    def test_country_filtered_for_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.country_filter)
        self.assertIn(self.mexico_instance, filtered_instances)

    def test_country_not_filtered_for_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.country_filter)
        self.assertNotIn(self.azerbaijan_instance, filtered_instances)


class DirectoryTopicFilterTest(TestCase):
    def setUp(self):
        self.directory = DirectoryPageFactory()
        # set up topics
        pf = TopicFactory(title='Press Freedom')
        irs = TopicFactory(title='IRS')
        pf.save()
        irs.save()
        # set up instances that are children of the directory and have those topics
        self.pf_instance = SecuredropPageFactory(parent=self.directory)
        self.pf_instance.topics.add(pf)
        self.pf_instance.save()

        self.irs_instance = SecuredropPageFactory(parent=self.directory)
        self.irs_instance.topics.add(irs)
        self.irs_instance.save()
        self.topic_filter = {'topics': pf}

    def test_topic_filtered_for_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.topic_filter)
        self.assertIn(self.pf_instance, filtered_instances)

    def test_topic_not_filtered_for_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.topic_filter)
        self.assertNotIn(self.irs_instance, filtered_instances)


class DirectorySearchFilterTest(TestCase):
    def setUp(self):
        self.directory = DirectoryPageFactory()
        self.best_instance = SecuredropPageFactory(
            title="Best Instansce",
            parent=self.directory
        )
        self.worst_instance = SecuredropPageFactory(
            title="Worst Instance",
            parent=self.directory
        )
        self.search_filter = {'title__icontains': 'best'}

    def test_title_searched_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.search_filter)
        self.assertIn(self.best_instance, filtered_instances)

    def test_title_not_searched_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.search_filter)
        self.assertNotIn(self.worst_instance, filtered_instances)


class DirectoryMultipleFiltersTest(TestCase):
    def setUp(self):
        self.directory = DirectoryPageFactory()
        # set up languages
        spanish = LanguageFactory(title='Spanish')
        chinese = LanguageFactory(title='Chinese')
        spanish.save()
        chinese.save()
        # set up countries
        mexico = CountryFactory(title='Mexico')
        azerbaijan = CountryFactory(title='Azerbaijan')
        mexico.save()
        azerbaijan.save()
        # set up topics
        pf = TopicFactory(title='Press Freedom')
        irs = TopicFactory(title='IRS')
        pf.save()
        irs.save()
        # set up instances that are children of the directory and have multiple categories
        self.sp_mx_instance = SecuredropPageFactory(parent=self.directory)
        self.sp_mx_instance.languages.add(spanish)
        self.sp_mx_instance.countries.add(mexico)
        self.sp_mx_instance.save()

        self.az_pf_instance = SecuredropPageFactory(parent=self.directory)
        self.az_pf_instance.countries.add(azerbaijan)
        self.az_pf_instance.topics.add(pf)
        self.az_pf_instance.save()

        self.other_instance = SecuredropPageFactory(parent=self.directory)
        self.other_instance.languages.add(spanish)
        self.other_instance.topics.add(pf)
        self.other_instance.save()

        # filters
        self.lang_country_filter = {
            'languages': spanish,
            'countries': mexico
        }

        self.country_topic_filter = {
            'countries': azerbaijan,
            'topics': pf
        }

    def test_country_and_language_filter(self):
        filtered_instances = self.directory.get_instances(filters=self.lang_country_filter)
        self.assertIn(self.sp_mx_instance, filtered_instances)
        self.assertNotIn(self.other_instance, filtered_instances)

    def test_country_and_topic_filter(self):
        filtered_instances = self.directory.get_instances(filters=self.country_topic_filter)
        self.assertIn(self.az_pf_instance, filtered_instances)
        self.assertNotIn(self.other_instance, filtered_instances)
