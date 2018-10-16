from unittest import TestCase, skip, mock

from bs4 import BeautifulSoup

from scanner.assets import (
    Asset,
    extract_assets,
    urls_from_css,
    urls_from_css_declarations,
)


class AssetExtractionTestCase(TestCase):
    def setUp(self):
        self.test_url = 'http://www.example.com'

    def test_should_extract_images(self):
        html = """
        <html><body><img src="image.jpg"></body></html>
        """
        soup = BeautifulSoup(html, "lxml")

        self.assertEqual([Asset(url='image.jpg', source='image')],
                         extract_assets(soup, self.test_url))

    def test_should_extract_external_scripts(self):
        html = """
        <html><head><script src="script.js"></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")

        self.assertEqual([Asset(url='script.js', source='external-js')],
                         extract_assets(soup, self.test_url))

    def test_should_extract_embedded_scripts_with_urls(self):
        html = """
        <html><head><script>var url = 'http://www.example.org';</script></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            extract_assets(soup, self.test_url),
            [Asset(url='http://www.example.org', source='embedded-js')],
        )

    def test_should_extract_urls_from_iframes(self):
        html = """
        <html><body><iframe src="https://www.example.org/embed.html"></iframe></body></html>
        """
        soup = BeautifulSoup(html, "lxml")

        self.assertEqual([
            Asset(
                url='https://www.example.org/embed.html',
                source='iframe'
            )],
            extract_assets(soup, self.test_url)
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_links_to_stylesheets(self, mock_requests):
        html = """
        <html><head><link href="/media/example.css" rel="stylesheet"></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual([Asset(url='/media/example.css', source='css-link')],
                         extract_assets(soup, self.test_url))

    def test_should_extract_urls_in_embedded_css(self):
        html = """<html><head><style>
        div {
          background-image: url("https://example.org/files/example.png");
        }
        </style></head><body></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual([
            Asset(
                url='https://example.org/files/example.png',
                source='css-embedded'
            )],
            extract_assets(soup, self.test_url)
        )

    def test_should_extract_urls_in_inline_css(self):
        html = """<html>
        <body style="background-image: url('https://example.org/files/example.png')"></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual([
            Asset(
                url='https://example.org/files/example.png',
                source='css-inline'
            )],
            extract_assets(soup, self.test_url)
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_urls_in_linked_css(self, requests_mock):
        requests_mock.get.return_value = mock.Mock(
            text='selector { background-image: url("https://example.org/example.png") }'
        )
        html = """
        <html><head><link href="https://example.org/styles.css" rel="stylesheet"></head><body></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            set(extract_assets(soup, self.test_url)), {
                Asset(url='https://example.org/styles.css', source='css-link'),
                Asset(url='https://example.org/example.png', source='css-link'),
            }
        )

    @skip
    def test_should_extract_urls_from_embedded_js(self):
        pass


class TestCssUrlExtractionFromDeclarations(TestCase):
    def test_should_extract_urls_from_css_declarations(self):
        css = 'background-image: url("http://www.example.com");'
        self.assertEqual(
            urls_from_css_declarations(css),
            ['http://www.example.com']
        )

    def test_should_extract_urls_from_multiproperty_declarations(self):
        css = "list-style: square url(http://www.example.com/redball.png);"
        self.assertEqual(urls_from_css_declarations(css),
                         ['http://www.example.com/redball.png'])


class TestCssUrlExtraction(TestCase):
    def test_should_extract_urls_from_at_import_rules(self):
        css = '@import url("thing.css");'
        self.assertEqual(urls_from_css(css), ['thing.css'])

    def test_should_extract_urls_from_multiple_selectors(self):
        css = """
              article {
                background-image: url(example.png);
              }
              section {
                background-image: url(example2.png);
              }
        """
        self.assertEqual(urls_from_css(css), ['example.png', 'example2.png'])

    def test_should_extract_urls_from_nested_at_rules(self):
        css = """
              @supports (display: flex) {
                @media screen and (min-width: 900px) {
                  article {
                    display: flex;
                    background-image: url("example.png");
                  }
                }
              }
        """
        self.assertEqual(urls_from_css(css), ['example.png'])

    def test_should_extract_urls_from_multiproperty_declarations(self):
        css = """"
              ul {
                list-style: square url(http://www.example.com/redball.png);
              }
        """
        self.assertEqual(urls_from_css(css),
                         ['http://www.example.com/redball.png'])
