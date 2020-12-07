from wagtail.admin.widgets import (
    ButtonWithDropdownFromHook,
    Button,
)
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)
from wagtail.core import hooks

from .models import ScanResult, DirectoryEntry


class ReadOnlyPermissionHelper(PermissionHelper):
    """Permission helper for read-only ModelAdmins
    Permission helper class that denies all permissions to modify,
    delete, or create objects.
    """
    def user_can_list(self, user):
        return True

    def user_can_create(self, user):
        return False

    def user_can_edit_obj(self, user, obj):
        return False

    def user_can_delete_obj(self, user, obj):
        return False


class ScanResultAdmin(ModelAdmin):
    model = ScanResult
    menu_icon = 'folder-open-inverse'
    menu_order = 500
    list_display = ('securedrop', 'result_last_seen', 'live', 'grade')
    list_filter = (
        'result_last_seen',
        'grade',
        'live',
    )
    search_fields = ('landing_page_url',)
    permission_helper_class = ReadOnlyPermissionHelper
    inspect_view_enabled = True


scanresult_modeladmin = ScanResultAdmin()


@hooks.register('register_page_listing_buttons')
def add_scan_results_buttons(page, page_perms, is_parent=False):
    """
    For directory entry pages, add an additional button to the page listing,
    linking to the most relevant model admin pages for scan results.
    """
    if isinstance(page, DirectoryEntry):
        yield ButtonWithDropdownFromHook(
            'Scan Results',
            hook_name='add_scan_results_button',
            page=page,
            page_perms=page_perms,
            is_parent=is_parent,
            priority=35
        )


@hooks.register('add_scan_results_button')
def add_bundle_stats_button(page, page_perms, is_parent=False):
    index_url = scanresult_modeladmin.url_helper.get_action_url('index')
    results_url = f'{index_url}?securedrop__page_ptr_id__exact={page.pk}'
    latest = page.get_live_result()
    return [
        Button(
            'All Results',
            results_url,
            priority=10,
        ),
        Button(
            'Latest Result',
            scanresult_modeladmin.url_helper.get_action_url('inspect', latest.pk),
            priority=20,
        )
    ]


modeladmin_register(ScanResultAdmin)
