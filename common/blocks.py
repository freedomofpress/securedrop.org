from django.utils.safestring import mark_safe

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from wagtail.wagtailcore import blocks
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock

from common.choices import BACKGROUND_COLOR_CHOICES


class Heading1(blocks.StructBlock):
    content = blocks.CharBlock()

    class Meta:
        template = 'common/blocks/heading_1.html'
        icon = 'title'
        label = 'Heading 1'


class Heading2(blocks.StructBlock):
    content = blocks.CharBlock()

    class Meta:
        template = 'common/blocks/heading_2.html'
        icon = 'title'
        label = 'Heading 2'


class Heading3(blocks.StructBlock):
    content = blocks.CharBlock()

    class Meta:
        template = 'common/blocks/heading_3.html'
        icon = 'title'
        label = 'Heading 3'


ALIGNMENT_CHOICES = (
    ('left', 'Left'),
    ('right', 'Right'),
    ('full-width', 'Full Width'),
)


class AlignedImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alignment = blocks.ChoiceBlock(choices=ALIGNMENT_CHOICES)

    class Meta:
        template = 'common/blocks/aligned_image.html'
        icon = 'image'
        label = 'Image'


class AlignedEmbedBlock(blocks.StructBlock):
    video = EmbedBlock()
    alignment = blocks.ChoiceBlock(choices=ALIGNMENT_CHOICES)

    class Meta:
        template = 'common/blocks/aligned_embed.html'
        icon = 'media'
        label = 'Video'


class StyledTextBlock(blocks.StructBlock):
    TEXT_ALIGN_CHOICES = (
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
    )

    FONT_SIZE_CHOICES = (
        ('small', 'Small'),
        ('normal', 'Normal'),
        ('large', 'Large'),
        ('jumbo', 'Jumbo'),
    )

    FONT_FAMILY_CHOICES = (
        ('sans-serif', 'Sans Serif'),
        ('serif', 'Serif'),
    )

    text = blocks.RichTextBlock()
    background_color = blocks.ChoiceBlock(choices=BACKGROUND_COLOR_CHOICES, default='white')
    text_align = blocks.ChoiceBlock(choices=TEXT_ALIGN_CHOICES, default='left')
    font_size = blocks.ChoiceBlock(choices=FONT_SIZE_CHOICES, default='normal')
    font_family = blocks.ChoiceBlock(choices=FONT_FAMILY_CHOICES, default='sans-serif')

    class Meta:
        template = 'common/blocks/styled_text.html'
        icon = 'doc-full'
        label = 'Styled Text Block'


class RichTextBlockQuoteBlock(blocks.StructBlock):
    text = blocks.RichTextBlock()
    source_text = blocks.RichTextBlock(required=False)
    source_url = blocks.URLBlock(required=False, help_text="Source text will link to this url.")

    class Meta:
        template = 'common/blocks/blockquote.html'
        icon = "openquote"


class CodeBlock(blocks.StructBlock):
    """
    Code Highlighting Block
    """
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('bash', 'Bash/Shell'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('scss', 'SCSS'),
        ('json', 'JSON'),
    )

    STYLE_CHOICES = (
        ('syntax', 'default'),
        ('emacs', 'emacs'),
        ('monokai', 'monokai'),
        ('vim', 'vim'),
        ('xcode', 'xcode'),
    )

    language = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES)
    style = blocks.ChoiceBlock(choices=STYLE_CHOICES, default='syntax')
    code = blocks.TextBlock()

    def render(self, value, **kwargs):
        src = value['code'].strip('\n')
        lang = value['language']
        lexer = get_lexer_by_name(lang)
        css_classes = ['code', value['style']]

        formatter = get_formatter_by_name(
            'html',
            linenos=None,
            cssclass=' '.join(css_classes),
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))

    class Meta:
        icon = 'code'
