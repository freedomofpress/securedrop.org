# Generated by Django 2.2.9 on 2020-01-21 20:44

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20190219_1839'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='body',
            field=wagtail.fields.StreamField([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'h2', 'h3', 'h4', 'ol', 'ul', 'hr', 'embed', 'link', 'document-link', 'image', 'code'])), ('code', wagtail.blocks.StructBlock([('language', wagtail.blocks.ChoiceBlock(choices=[('python', 'Python'), ('bash', 'Bash/Shell'), ('html', 'HTML'), ('css', 'CSS'), ('scss', 'SCSS'), ('json', 'JSON')])), ('code', wagtail.blocks.TextBlock())], label='Code Block')), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('alignment', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')]))])), ('raw_html', wagtail.blocks.RawHTMLBlock()), ('blockquote', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock()), ('source_text', wagtail.blocks.RichTextBlock(required=False)), ('source_url', wagtail.blocks.URLBlock(help_text='Source text will link to this url.', required=False))])), ('list', wagtail.blocks.ListBlock(wagtail.blocks.CharBlock(label='List Item'), template='common/blocks/list_block_columns.html')), ('video', wagtail.blocks.StructBlock([('video', wagtail.embeds.blocks.EmbedBlock()), ('alignment', wagtail.blocks.ChoiceBlock(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')]))])), ('heading_1', wagtail.blocks.StructBlock([('content', wagtail.blocks.CharBlock())])), ('heading_2', wagtail.blocks.StructBlock([('content', wagtail.blocks.CharBlock())])), ('heading_3', wagtail.blocks.StructBlock([('content', wagtail.blocks.CharBlock())]))]),
        ),
    ]
