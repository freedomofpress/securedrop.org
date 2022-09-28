import os

from wagtail.tests.utils import WagtailPageTests

from directory.models import ScanResult
from directory.wagtail_hooks import ScanResultAdmin
from scanner.tests.test_scanner import mod_vcr


VCR_DIR = os.path.join(os.path.dirname(__file__), 'scans_vcr')


class ManualScanTests(WagtailPageTests):
    def setUp(self):
        super().setUp()

        self.admin = ScanResultAdmin()
        self.view_url = self.admin.url_helper.create_url

    def test_getting_the_form_succeeds(self):
        response = self.client.get(self.view_url)
        self.assertEqual(response.status_code, 200)

    @mod_vcr.use_cassette(
        os.path.join(VCR_DIR, 'manual-scan.yaml'),
        # Workaround for flickering test, see:
        # https://github.com/kevin1024/vcrpy/issues/533
        allow_playback_repeats=True,
    )
    def test_creates_new_scan_result(self):
        landing_page_url = 'https://www.nytimes.com/tips'

        response = self.client.post(
            self.view_url,
            {'landing_page_url': landing_page_url},
        )

        result = ScanResult.objects.get(landing_page_url=landing_page_url)

        self.assertEqual(response.status_code, 302)
        expected_url = self.admin.url_helper.get_action_url(
            'inspect',
            result.pk,
        )
        self.assertEqual(response.url, expected_url)
