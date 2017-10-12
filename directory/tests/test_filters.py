from django.test import TestCase

from directory.tests.factories import DirectoryPageFactory, LanguageFactory

from landing_page_checker.tests.factories import SecuredropPageFactory


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
        self.lang_filter = { 'languages': spanish }

    def test_language_filtered_for_is_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.lang_filter)
        self.assertIn(self.spanish_instance, filtered_instances)

    def test_langauge_not_filtered_for_is_not_in_queryset(self):
        filtered_instances = self.directory.get_instances(filters=self.lang_filter)
        self.assertNotIn(self.chinese_instance, filtered_instances)
