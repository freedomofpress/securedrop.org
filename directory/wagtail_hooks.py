from django.utils.translation import ugettext as _
from wagtail.admin.widgets import (
    ButtonWithDropdownFromHook,
    Button,
)
from wagtail.contrib.modeladmin.helpers import PermissionHelper, ButtonHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
)
from wagtail.core import hooks

from .models import ScanResult, DirectoryEntry
from .views import ManualScanView


class CannotModifyPermissionHelper(PermissionHelper):
    """Permission helper for read-only ModelAdmins

    Permission helper class that denies all permissions to edit or
    delete objects.

    """
    def user_can_list(self, user):
        return True

    def user_can_edit_obj(self, user, obj):
        return False

    def user_can_delete_obj(self, user, obj):
        return False


class MyButtonHelper(ButtonHelper):
    def add_button(self, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.add_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.create_url,
            'label': _('Perform a scan'),
            'classname': cn,
            'title': _('Perform a scan'),
        }


class ScanResultAdmin(ModelAdmin):
    """ModelAdmin for viewing/searching ScanResults."""
    model = ScanResult
    button_helper_class = MyButtonHelper
    create_view_class = ManualScanView
    menu_icon = 'folder-open-inverse'
    menu_order = 500
    list_display = ('securedrop', 'landing_page_url', 'result_last_seen', 'live', 'grade')
    list_filter = (
        'result_last_seen',
        'grade',
        'live',
    )
    search_fields = ('landing_page_url', 'securedrop__title')
    permission_helper_class = CannotModifyPermissionHelper
    inspect_view_enabled = True


scanresult_modeladmin = ScanResultAdmin()


@hooks.register('register_page_listing_buttons')
def add_scan_results_buttons(page, page_perms, is_parent=False, next_url=None):
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
def add_bundle_stats_button(page, page_perms, is_parent=False, next_url=None):
    """Creates drop-down buttons that link to ScanResult model admin
    sections for a given DirectoryEntry on the page listing area.  The
    links go to the most recent live result, as well as the filtered
    list of all results.

    """
    index_url = scanresult_modeladmin.url_helper.get_action_url('index')
    results_url = f'{index_url}?securedrop__page_ptr_id__exact={page.pk}'
    buttons = [
        Button(
            'All Results',
            results_url,
            priority=10,
        )
    ]
    latest = page.get_live_result()
    if latest and latest.pk:
        buttons.append(
            Button(
                'Latest Result',
                scanresult_modeladmin.url_helper.get_action_url('inspect', latest.pk),
                priority=20,
            )
        )
    return buttons


modeladmin_register(ScanResultAdmin)
