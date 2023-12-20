from django.utils.translation import gettext as _
from wagtail.admin.ui.tables import BooleanColumn
from wagtail.admin.widgets import (
    ButtonWithDropdownFromHook,
    Button,
)
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail import hooks

from .models import ScanResult, DirectoryEntry
from .views import ManualScanView


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


class ScanResultAdmin(SnippetViewSet):
    """SnippetViewSet for viewing/searching ScanResults."""
    model = ScanResult
    action_text = _('Perform a scan')
    add_view_class = ManualScanView
    # create_template_name = 'modeladmin/scan_form.html'
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


@hooks.register('register_page_listing_buttons')
def add_scan_results_buttons(page, user, next_url=None):
    """
    For directory entry pages, add an additional button to the page listing,
    linking to the most relevant model admin pages for scan results.
    """
    if isinstance(page, DirectoryEntry):
        yield ButtonWithDropdownFromHook(
            'Scan Results',
            hook_name='add_scan_results_button',
            page=page,
            user=user,
            priority=35
        )


@hooks.register('add_scan_results_button')
def button_for_scan_results(page, page_perms, next_url=None):
    """Creates drop-down buttons that link to ScanResult model admin
    sections for a given DirectoryEntry on the page listing area.  The
    links go to the most recent live result, as well as the filtered
    list of all results.

    """
    index_url = scanresult_snippetviewset.url_helper.get_action_url('index')
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
                scanresult_snippetviewset.url_helper.get_action_url('inspect', latest.pk),
                priority=20,
            )
        )
    return buttons


register_snippet(ScanResultAdmin)
