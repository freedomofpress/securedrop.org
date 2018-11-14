from unittest import TestCase

from scanner.utils import url_to_domain, extract_strings, extract_urls


class URLToDomainTestCase(TestCase):
    def test_url_to_domain_strips_protocol(self):
        url = 'https://securedrop.org'
        self.assertEqual(url_to_domain(url), 'securedrop.org')

    def test_url_to_domain_strips_path(self):
        url = 'securedrop.org/path/'
        self.assertEqual(url_to_domain(url), 'securedrop.org')

    def test_url_to_domain_strips_path_and_protocol(self):
        url = 'https://securedrop.org/path/'
        self.assertEqual(url_to_domain(url), 'securedrop.org')


class StringExtractionTestCase(TestCase):
    def test_should_extract_unique_strings_from_js_block(self):
        js = """var _comscore = _comscore || [];
  _comscore.push({ c1: "2", c2: "111111", c3: '222222' });
  (function() {
    var s = document.createElement("script"), el = document.getElementsByTagName("script")[0]; s.async = true;
    s.src = (document.location.protocol == "https:" ? "https://sb" : "http://b") + ".example.com/beacon.js";
    el.parentNode.insertBefore(s, el);
  })();"""

        expected = {
            '2',
            '111111',
            '222222',
            'script',
            'https:',
            'https://sb',
            'http://b',
            '.example.com/beacon.js',
        }
        self.assertEqual(extract_strings(js), expected)


class UrlExtractionTestCase(TestCase):
    def test_should_extract_urls_from_a_string(self):
        self.assertEqual(
            extract_urls('http://www.example.com'),
            ['http://www.example.com'],
        )

        self.assertEqual(extract_urls('www.example.com, www.example2.com'),
                         ['www.example.com', 'www.example2.com'])

        self.assertEqual(extract_urls('.example.com'), ['example.com'])
        self.assertEqual(extract_urls('//cdn.example.com'), ['cdn.example.com'])
        self.assertEqual(extract_urls('//www.example.com/file.js?id='),
                         ['www.example.com/file.js?id='])
