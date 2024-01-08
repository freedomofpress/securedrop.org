from django.utils.translation import gettext as _
from django.urls import path, reverse
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.tables import BooleanColumn
from wagtail.admin.widgets import (
    ButtonWithDropdownFromHook,
    Button,
)
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail import hooks

from .models import ScanResult, DirectoryEntry
from .views import ManualScanView


class ScanResultAdmin(SnippetViewSet):
    """SnippetViewSet for viewing/searching ScanResults."""
    model = ScanResult
    action_text = _('Perform a scan')
    # add_view_class = ManualScanView
    # # create_template_name = 'modeladmin/scan_form.html'
    add_to_admin_menu = True
    icon = 'folder-open-inverse'
    menu_order = 500
    list_display = (
        'securedrop',
        'landing_page_url',
        'result_last_seen',
        BooleanColumn('live'),
        'grade'
    )
    list_filter = (
        'result_last_seen',
        'grade',
        'live',
    )
    search_fields = ('landing_page_url', 'securedrop__title')
    inspect_view_enabled = True


scanresult_snippetviewset = ScanResultAdmin()


@hooks.register('construct_snippet_listing_buttons')
def remove_snippet_listing_button_item(buttons, snippet, user):
    """
    Removes edit and delete from the action buttons of each snippet
    """
    buttons[:] = [button for button in buttons if button.label not in ('Delete', 'Edit')]


register_snippet(ScanResultAdmin)


@hooks.register('register_admin_urls')
def manual_scan_url():
    return [
        path(
            'manual_scan/',
            ManualScanView.as_view(),
            name='manual_scan'
        )
    ]


@hooks.register('register_admin_menu_item')
def register_manual_scan_item():
    return MenuItem(
        'Perform a scan',
        reverse('manual_scan'),
        classnames='icon icon-plus',
    )
