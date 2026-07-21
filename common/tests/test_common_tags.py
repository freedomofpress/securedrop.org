from django.test import SimpleTestCase

from common.templatetags.common_tags import richtext_inline


class TestRichtextInline(SimpleTestCase):
    def test_allowed_tags_preserved(self):
        result = richtext_inline("<p>Hello <strong>world</strong></p>")
        self.assertIn("<strong>world</strong>", result)

    def test_disallowed_tag_stripped_content_kept(self):
        result = richtext_inline('<script>alert("xss")</script>safe text')
        self.assertNotIn("<script>", result)
        self.assertIn("safe text", result)

    def test_link_href_preserved(self):
        result = richtext_inline('<a href="https://example.com">link</a>')
        self.assertIn('href="https://example.com"', result)

    def test_abbr_title_preserved(self):
        result = richtext_inline('<abbr title="HyperText Markup Language">HTML</abbr>')
        self.assertIn('title="HyperText Markup Language"', result)

    def test_disallowed_attribute_stripped(self):
        result = richtext_inline(
            '<a href="https://example.com" onclick="alert(1)">link</a>'
        )
        self.assertNotIn("onclick", result)
        self.assertIn('href="https://example.com"', result)

    def test_block_level_tags_stripped(self):
        result = richtext_inline("<p>paragraph</p>")
        self.assertNotIn("<p>", result)
        self.assertIn("paragraph", result)
