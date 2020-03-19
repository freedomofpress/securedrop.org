# Generated by Django 2.2.9 on 2020-02-03 17:39

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('simple', '0002_auto_20190219_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faqpage',
            name='body',
            field=wagtail.core.fields.StreamField([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'h2', 'h3', 'h4', 'ol', 'ul', 'hr', 'embed', 'link', 'document-link', 'image', 'code'])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')]))])), ('raw_html', wagtail.core.blocks.RawHTMLBlock()), ('blockquote', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock()), ('source_text', wagtail.core.blocks.RichTextBlock(required=False)), ('source_url', wagtail.core.blocks.URLBlock(help_text='Source text will link to this url.', required=False))])), ('list', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('video', wagtail.core.blocks.StructBlock([('video', wagtail.embeds.blocks.EmbedBlock()), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')]))])), ('heading_1', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())])), ('heading_2', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())])), ('heading_3', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())]))], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='simplepage',
            name='body',
            field=wagtail.core.fields.StreamField([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'h2', 'h3', 'h4', 'ol', 'ul', 'hr', 'embed', 'link', 'document-link', 'image', 'code'])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')]))])), ('raw_html', wagtail.core.blocks.RawHTMLBlock()), ('blockquote', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock()), ('source_text', wagtail.core.blocks.RichTextBlock(required=False)), ('source_url', wagtail.core.blocks.URLBlock(help_text='Source text will link to this url.', required=False))])), ('list', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('video', wagtail.core.blocks.StructBlock([('video', wagtail.embeds.blocks.EmbedBlock()), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')]))])), ('heading_1', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())])), ('heading_2', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())])), ('heading_3', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())]))]),
        ),
        migrations.AlterField(
            model_name='simplepagewithmenusidebar',
            name='body',
            field=wagtail.core.fields.StreamField([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'h2', 'h3', 'h4', 'ol', 'ul', 'hr', 'embed', 'link', 'document-link', 'image', 'code'])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')]))])), ('raw_html', wagtail.core.blocks.RawHTMLBlock()), ('blockquote', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock()), ('source_text', wagtail.core.blocks.RichTextBlock(required=False)), ('source_url', wagtail.core.blocks.URLBlock(help_text='Source text will link to this url.', required=False))])), ('list', wagtail.core.blocks.ListBlock(wagtail.core.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('video', wagtail.core.blocks.StructBlock([('video', wagtail.embeds.blocks.EmbedBlock()), ('alignment', wagtail.core.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')]))])), ('heading_1', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())])), ('heading_2', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())])), ('heading_3', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.CharBlock())]))]),
        ),
    ]