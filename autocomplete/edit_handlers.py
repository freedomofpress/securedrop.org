from django.apps import apps

from wagtail.wagtailadmin.edit_handlers import (
    BaseFieldPanel,
    BaseChooserPanel,
)

from .widgets import Autocomplete


def _can_create(page_type):
    """Returns True if the given model has implemented the autocomplete_create
    method to allow new instances to be creates from a single string value.
    """
    return callable(getattr(
        apps.get_model(page_type),
        'autocomplete_create',
        None,
    ))


class AutocompleteFieldPanel:
    def __init__(self, field_name, page_type='wagtailcore.Page'):
        self.field_name = field_name
        self.page_type = page_type

    def bind_to_model(self, model):
        can_create = _can_create(self.page_type)
        base = dict(
            model=model,
            field_name=self.field_name,
            widget=type(
                '_Autocomplete',
                (Autocomplete,),
                dict(page_type=self.page_type, can_create=can_create, is_single=False),
            ),
        )
        return type('_AutocompleteFieldPanel', (BaseFieldPanel,), base)


class AutocompletePageChooserPanel:
    def __init__(self, field_name, page_type='wagtailcore.Page'):
        self.field_name = field_name
        self.page_type = page_type

    def bind_to_model(self, model):
        # TODO: support list of page types
        model = apps.get_model(self.page_type)
        can_create = _can_create(self.page_type)

        base = dict(
            model=model,
            field_name=self.field_name,
            page_type=self.page_type,
            object_type_name=model._meta.verbose_name,
            widget=type(
                '_Autocomplete',
                (Autocomplete,),
                dict(page_type=self.page_type, can_create=can_create, is_single=True)
            )
        )
        return type('_AutocompletePageChooserPanel', (BaseChooserPanel,), base)
