from unittest.mock import patch

from django.test import TestCase

from wagtail.admin.rich_text import get_rich_text_editor_widget
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler,
)


class TestRichTextParsing(TestCase):
    def test_embed_in_a_tag(self):
        """block tags nested inside block tags should parse without errors"""
        converter = get_rich_text_editor_widget().converter

        nested_block_embed = "<b><p>Hi</p></b>"
        # This line should not raise an exception
        converter.from_database_format(nested_block_embed)

    # The test below is to let us know when/if a bug is fixed within
    # wagtail.  If this test fails, then the bug has been fixed.  In
    # it we revert the monkey-patching of our fixed method and attempt
    # the parsing using the native wagtail method.  If it does not
    # raise an exception, then the test fails and we will notice the
    # bug is fixed.
    @patch.object(BlockElementHandler, 'handle_endtag', BlockElementHandler.fpf_old_handle_endtag)
    def test_wagtail_fails_to_parse_embed_in_a_tag(self):
        converter = get_rich_text_editor_widget().converter
        nested_block_embed = '<b><p>Hi</p></b>'

        with self.assertRaises(AssertionError):
            converter.from_database_format(nested_block_embed)
