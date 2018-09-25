import random
import string
from datetime import datetime

import factory

import wagtail_factories
from directory.models import DirectoryEntry, ScanResult
from directory.tests.factories.taxonomy import (
    LanguageFactory,
    CountryFactory,
    TopicFactory,
)


def random_onion_address():
    return 'https://' + ''.join(
        random.choice(string.ascii_lowercase + string.digits)
        for _ in range(16)
    ) + '.onion'


class DirectoryEntryFactory(wagtail_factories.PageFactory):
    class Meta:
        model = DirectoryEntry

    title = factory.Faker('sentence', nb_words=3)
    landing_page_url = factory.Faker('uri')
    onion_address = factory.LazyFunction(random_onion_address)
    parent = None

    @factory.post_generation
    def languages(self, create, count):
        if count is None:
            count = 2
        make_language = getattr(LanguageFactory, 'create' if create else 'build')
        languages = []
        for i in range(count):
            lang = make_language()
            lang.save()
            lang.languages.add(self)
            languages.append(lang)
        if not create:
            self._prefetched_objects_cache = {'languages': languages}

    @factory.post_generation
    def countries(self, create, count):
        if count is None:
            count = 2
        make_country = getattr(CountryFactory, 'create' if create else 'build')
        countries = []
        for i in range(count):
            country = make_country()
            country.save()
            country.countries.add(self)
            countries.append(country)
        if not create:
            self._prefetched_objects_cache = {'countries': countries}

    @factory.post_generation
    def topics(self, create, count):
        if count is None:
            count = 2
        make_topic = getattr(TopicFactory, 'create' if create else 'build')
        topics = []
        for i in range(count):
            topic = make_topic()
            topic.save()
            topic.topics.add(self)
            topics.append(topic)
        if not create:
            self._prefetched_objects_cache = {'topics': topics}


class ScanResultFactory(factory.Factory):
    class Meta:
        model = ScanResult

    class Params:
        no_failures = factory.Trait(
            live=True,
            result_last_seen=datetime.today(),
            forces_https=True,
            hsts=True,
            hsts_max_age=True,
            hsts_entire_domain=True,
            hsts_preloaded=True,
            http_status_200_ok=True,
            http_no_redirect=True,
            expected_encoding=True,
            no_server_info=True,
            no_server_version=True,
            csp_origin_only=True,
            mime_sniffing_blocked=True,
            noopen_download=True,
            xss_protection=True,
            clickjacking_protection=True,
            good_cross_domain_policy=True,
            http_1_0_caching_disabled=True,
            cache_control_set=True,
            cache_control_revalidate_set=True,
            cache_control_nocache_set=True,
            cache_control_notransform_set=True,
            cache_control_nostore_set=True,
            cache_control_private_set=True,
            expires_set=True,
            referrer_policy_set_to_no_referrer=True,
            safe_onion_address=True,
            no_cdn=True,
            no_analytics=True,
            subdomain=False,
            no_cookies=True,
        )
        moderate_warning = factory.Trait(
            no_failures=True,
            safe_onion_address=False,
        )
        severe_warning = factory.Trait(
            no_failures=True,
            no_analytics=False,
        )
