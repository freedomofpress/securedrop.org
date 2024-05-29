from unittest import TestCase, mock

from bs4 import BeautifulSoup

from scanner.assets import (
    Asset,
    extract_assets,
    fetch_asset,
    parse_srcset,
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

        self.assertEqual(
            [Asset(resource='image.jpg', kind='img-src', initiator=self.test_url)],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_images_from_srcset(self):
        html = """
        <html><body><img srcset="image-320w.jpg 320w,
             image-480w.jpg 480w,
             image-800w.jpg 800w"></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [
                Asset(
                    resource='image-320w.jpg',
                    kind='img-srcset',
                    initiator=self.test_url,
                ),
                Asset(
                    resource='image-480w.jpg',
                    kind='img-srcset',
                    initiator=self.test_url,
                ),
                Asset(
                    resource='image-800w.jpg',
                    kind='img-srcset',
                    initiator=self.test_url,
                ),
            ],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_urls_from_sources(self):
        html = """<html><body>
        <video>
        <source src="video.webm" type="video/webm">
        <source src="video.ogg" type="video/ogg">
        <source src="video.mov" type="video/quicktime">
        </video></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [
                Asset(
                    resource='video.webm', kind='source-src', initiator=self.test_url
                ),
                Asset(resource='video.ogg', kind='source-src', initiator=self.test_url),
                Asset(resource='video.mov', kind='source-src', initiator=self.test_url),
            ],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_urls_from_embeds(self):
        html = """<html><body><embed type="video/quicktime" src="movie.mov" width="640" height="480"></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [Asset(resource='movie.mov', kind='embed-src', initiator=self.test_url)],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_urls_from_video(self):
        html = """<html><body>
        <video controls
               src="https://archive.org/download/BigBuckBunny_124/Content/big_buck_bunny_720p_surround.mp4"
               poster="https://peach.blender.org/wp-content/uploads/title_anouncement.jpg?x11217"
               width="620"></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [
                Asset(
                    resource='https://archive.org/download/BigBuckBunny_124/Content/big_buck_bunny_720p_surround.mp4',
                    kind='video-src',
                    initiator=self.test_url,
                ),
                Asset(
                    resource='https://peach.blender.org/wp-content/uploads/title_anouncement.jpg?x11217',
                    kind='video-poster',
                    initiator=self.test_url,
                ),
            ],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_urls_from_audio(self):
        html = """<html><body><audio src="audio.wav"></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [Asset(resource='audio.wav', kind='audio-src', initiator=self.test_url)],
            extract_assets(soup, self.test_url),
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_external_scripts(self, mock_requests):
        mock_requests.get.return_value = mock.Mock(text='')
        html = """
        <html><head><script src="script.js"></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")

        self.assertEqual(
            [Asset(resource='script.js', kind='script-src', initiator=self.test_url)],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_embedded_scripts_with_urls(self):
        html = """
        <html><head><script>var url = 'http://www.example.org';</script></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            extract_assets(soup, self.test_url),
            [
                Asset(
                    resource='http://www.example.org',
                    kind='script-embed',
                    initiator=self.test_url,
                )
            ],
        )

    def test_should_extract_urls_from_iframes(self):
        html = """
        <html><body><iframe src="https://www.example.org/embed.html"></iframe></body></html>
        """
        soup = BeautifulSoup(html, "lxml")

        self.assertEqual(
            [
                Asset(
                    resource='https://www.example.org/embed.html',
                    kind='iframe-src',
                    initiator=self.test_url,
                )
            ],
            extract_assets(soup, self.test_url),
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_links_to_stylesheets(self, mock_requests):
        html = """
        <html><head><link href="/media/example.css" rel="stylesheet"></head><body></body></html>
        """

        soup = BeautifulSoup(html, "lxml")

        self.assertEqual(
            [
                Asset(
                    resource='/media/example.css',
                    kind='style-href',
                    initiator=self.test_url,
                )
            ],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_urls_in_embedded_css(self):
        html = """<html><head><style>
        div {
          background-image: url(https://example.org/files/example.png);
        }
        </style></head><body></body></html>"""

        soup = BeautifulSoup(html, "lxml")

        self.assertEqual(
            [
                Asset(
                    resource='https://example.org/files/example.png',
                    kind='style-embed',
                    initiator=self.test_url,
                )
            ],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_string_urls_in_embedded_css(self):
        html = """<html><head><style>
        div {
          background-image: url("https://example.org/files/example.png");
        }
        </style></head><body></body></html>"""

        soup = BeautifulSoup(html, "lxml")

        self.assertEqual(
            [
                Asset(
                    resource='https://example.org/files/example.png',
                    kind='style-embed',
                    initiator=self.test_url,
                )
            ],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_urls_in_inline_css(self):
        html = """<html>
        <body style="background-image: url(https://example.org/files/example.png)"></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [
                Asset(
                    resource='https://example.org/files/example.png',
                    kind='style-resource-inline',
                    initiator=self.test_url,
                )
            ],
            extract_assets(soup, self.test_url),
        )

    def test_should_extract_string_urls_in_inline_css(self):
        html = """<html>
        <body style="background-image: url('https://example.org/files/example.png')"></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [
                Asset(
                    resource='https://example.org/files/example.png',
                    kind='style-resource-inline',
                    initiator=self.test_url,
                )
            ],
            extract_assets(soup, self.test_url),
        )

    def test_should_handle_unfetchable_urls(self):
        html = """<html><head>
        <link rel="stylesheet" href="file:///Users/dcao/Downloads/securedrop.css">
        </head><body></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [
                Asset(
                    resource='file:///Users/dcao/Downloads/securedrop.css',
                    kind='style-href',
                    initiator=self.test_url,
                )
            ],
            extract_assets(soup, self.test_url),
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_urls_in_linked_css(self, requests_mock):
        requests_mock.get.return_value = mock.Mock(
            text='selector { background-image: url(https://example.org/example.png) }'
        )
        html = """
        <html><head><link href="https://example.org/styles.css" rel="stylesheet"></head><body></body></html>"""
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            set(extract_assets(soup, self.test_url)),
            {
                Asset(
                    resource='https://example.org/styles.css',
                    kind='style-href',
                    initiator=self.test_url,
                ),
                Asset(
                    resource='https://example.org/example.png',
                    kind='style-resource',
                    initiator='https://example.org/styles.css',
                ),
            },
        )

    @mock.patch('scanner.assets.requests')
    def test_should_extract_urls_in_external_js(self, mock_requests):
        mock_requests.get.return_value = mock.Mock(
            text="""function makeRequest() { $.getJSON('http://example.org/', function(data) {}); }"""
        )

        html = """
        <html><head><script src="file.js"></head><body></body></html>
        """
        soup = BeautifulSoup(html, "lxml")
        self.assertEqual(
            [
                Asset(resource='file.js', kind='script-src', initiator=self.test_url),
                Asset(
                    resource='http://example.org/',
                    kind='script-resource',
                    initiator='file.js',
                ),
            ],
            extract_assets(soup, self.test_url),
        )


class TestAssetFetching(TestCase):
    @mock.patch('scanner.assets.requests.get')
    def test_should_send_headers_in_request_for_assets(self, requests_get):
        asset_url = 'example.gif'
        site_url = 'http://example.com'
        fetch_asset(asset_url, site_url)

        requests_get.assert_called_once_with(
            'http://example.com/example.gif',
            headers={'User-Agent': 'SecureDrop Landing Page Scanner 0.1.0'},
            timeout=5,
        )


class TestCssUrlExtractionFromDeclarations(TestCase):
    def test_should_extract_urls_from_css_declarations(self):
        css = 'background-image: url(http://www.example.com);'
        self.assertEqual(urls_from_css_declarations(css), ['http://www.example.com'])

    def test_should_extract_urls_from_multiproperty_declarations(self):
        css = "list-style: square url(http://www.example.com/redball.png);"
        self.assertEqual(
            urls_from_css_declarations(css), ['http://www.example.com/redball.png']
        )


class TestCssUrlExtraction(TestCase):
    def test_should_extract_urls_from_at_import_rules(self):
        css = '@import url(thing.css);'
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
                    background-image: url(example.png);
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
        self.assertEqual(urls_from_css(css), ['http://www.example.com/redball.png'])


class TestSrcSetExtraction(TestCase):
    def test_should_extract_nothing_from_empty_srcset(self):
        self.assertEqual(parse_srcset(''), [])

    def test_should_extract_urls_from_srcset(self):
        self.assertEqual(
            parse_srcset('image-1x.png 1x, image-2x.png 2x'),
            ['image-1x.png', 'image-2x.png'],
        )

    def test_should_extract_urls_with_extra_whitespace(self):
        self.assertEqual(
            parse_srcset('image-1x.png  1x, image-2x.png  2x'),
            ['image-1x.png', 'image-2x.png'],
        )

    def test_should_extract_urls_with_no_sizes(self):
        self.assertEqual(
            parse_srcset('image-1x.png, image-2x.png'), ['image-1x.png', 'image-2x.png']
        )
