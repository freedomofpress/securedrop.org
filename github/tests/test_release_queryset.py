from datetime import UTC, datetime

from django.test import TestCase

from github.factories import ProductFactory, ReleaseFactory
from github.models import Release


class LatestPerVisibleProductTestCase(TestCase):
    def setUp(self):
        self.apple = ProductFactory(
            name="Apple", repo_full_name="fp/apple", sort_order=1
        )
        self.banana = ProductFactory(
            name="Banana", repo_full_name="fp/banana", sort_order=2
        )

    def _release(self, product, year, tag):
        return ReleaseFactory(
            product=product,
            tag_name=tag,
            date=datetime(year, 1, 1, tzinfo=UTC),
        )

    def test_returns_only_the_latest_release_per_product(self):
        self._release(self.apple, 2019, "a-old")
        latest_a = self._release(self.apple, 2021, "a-new")
        latest_b = self._release(self.banana, 2020, "b-new")

        self.assertEqual(
            list(Release.objects.latest_per_visible_product()),
            [latest_a, latest_b],
        )

    def test_ordered_by_product_sort_order_not_release_date(self):
        # banana's release is newer, but apple sorts first by sort_order.
        self._release(self.banana, 2021, "b")
        self._release(self.apple, 2019, "a")

        results = list(Release.objects.latest_per_visible_product())
        self.assertEqual([r.product for r in results], [self.apple, self.banana])

    def test_excludes_products_with_show_releases_false(self):
        self.banana.show_releases = False
        self.banana.save()
        self._release(self.apple, 2021, "a")
        self._release(self.banana, 2021, "b")

        results = list(Release.objects.latest_per_visible_product())
        self.assertEqual([r.product for r in results], [self.apple])
