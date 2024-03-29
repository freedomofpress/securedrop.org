from django.utils.safestring import mark_safe

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


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
    ('center', 'Center'),
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
        label = 'Embed Video Link'


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

    language = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES)
    code = blocks.TextBlock()

    def render(self, value, **kwargs):
        src = value['code'].strip('\n')
        lang = value['language']
        lexer = get_lexer_by_name(lang)
        css_classes = ['code', 'syntax']

        formatter = get_formatter_by_name(
            'html',
            linenos=None,
            cssclass=' '.join(css_classes),
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))  # nosec

    class Meta:
        icon = 'code'


class InlinePDFBlock(blocks.StructBlock):
    document = DocumentChooserBlock(required=True)

    class Meta:
        template = 'common/blocks/inline_pdf.html'
        icon = 'doc-full'
        label = 'Inline PDF'


class MediaBlock(AbstractMediaChooserBlock):
    class Meta:
        template = 'common/blocks/media.html'


class VideoBlock(blocks.StructBlock):
    class Meta:
        template = 'common/blocks/video.html'
        icon = 'media'
        label = 'Video file'

    media = MediaBlock()
    muted_autoplay_and_loop = blocks.BooleanBlock(
        required=False,
        help_text='If checked, the media will start playing, without sound, when the page loads and loop when finished. Intended to allow videos to function as GIFs.'
    )
