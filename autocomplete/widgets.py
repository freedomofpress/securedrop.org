import json

from django.apps import apps
from django.forms import Widget
from django.utils.html import format_html

from wagtail.wagtailcore import hooks
from webpack_loader.utils import get_loader

from .views import render_page


@hooks.register('insert_editor_js')
def editor_js():
    chunks = get_loader('DEFAULT').get_bundle('editor')
    chunk = next(filter(lambda chunk: chunk['name'].endswith('.js'), chunks))
    if not chunk:
        return ''
    html = '<script type="text/javascript" src="{}"></script>'.format(chunk['url'])
    return format_html(html)


@hooks.register('insert_editor_css')
def editor_css():
    chunks = get_loader('DEFAULT').get_bundle('editor')
    chunk = next(filter(lambda chunk: chunk['name'].endswith('.css'), chunks))
    if not chunk:
        return ''
    html = '<link rel="stylesheet" type="text/css" href="{}" />'.format(chunk['url'])
    return format_html(html)


class Autocomplete(Widget):
    template_name = 'autocomplete/autocomplete.html'

    def get_context(self, *args, **kwargs):
        context = super(Autocomplete, self).get_context(*args, **kwargs)
        context['widget']['page_type'] = self.page_type
        context['widget']['can_create'] = self.can_create
        context['widget']['is_single'] = self.is_single
        return context

    def format_value(self, value):
        if not value:
            return 'null'

        model = apps.get_model(self.page_type)
        if type(value) == list:
            return json.dumps([render_page(page) for page in model.objects.filter(id__in=value)])
        else:
            return json.dumps(render_page(model.objects.get(pk=value)))

    def value_from_datadict(self, data, files, name):
        value = json.loads(data.get(name))
        if not value:
            return None

        if type(value) == list:
            return [obj['id'] for obj in value]

        return value['id']
