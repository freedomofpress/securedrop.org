from django.utils.translation import gettext as _
from django.urls import path, reverse
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.tables import BooleanColumn
from wagtail.admin.widgets import (
    ButtonWithDropdownFromHook,
    Button,
)
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail import hooks

from .models import ScanResult, DirectoryEntry
from .views import ManualScanView


class ScanResultAdmin(ModelViewSet):
    """SnippetViewSet for viewing/searching ScanResults."""
    model = ScanResult
    add_to_admin_menu = True
    icon = 'folder-open-inverse'
    menu_order = 500
    form_fields = []
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

    def get_common_view_kwargs(self, **kwargs):
        view_kwargs = super().get_common_view_kwargs(
            **{
                "add_url_name": None,
                "edit_url_name": None,
                "delete_url_name": None,
                **kwargs,
            }
        )
        if self.inspect_view_enabled:
            view_kwargs["inspect_url_name"] = self.get_url_name("inspect")
        return view_kwargs


scanresult_viewset = ScanResultAdmin()


@hooks.register('register_admin_viewset')
def register_scanresult_viewset():
    return scanresult_viewset


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
        classname='icon icon-plus',
    )
