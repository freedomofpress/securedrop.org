from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from wagtail.snippets.views.snippets import CreateView

from scanner.scanner import perform_scan

from .forms import ManualScanForm


class ManualScanView(CreateView, FormView):
    model_admin = None
    template_name = 'modeladmin/scan_form.html'
    form_class = ManualScanForm
    page_title = 'Manual Scan'

    def get_page_title(self):
        return self.page_title

    def get_meta_title(self):
        return self.get_page_title()

    def form_valid(self, form):
        from .wagtail_hooks import ScanResultAdmin

        scanresult_modeladmin = ScanResultAdmin()

        permitted_domains = form.cleaned_data['permitted_domains'].split(',')
        landing_page_url = form.cleaned_data['landing_page_url']

        result = perform_scan(landing_page_url, permitted_domains)
        result.save()

        result_url = scanresult_modeladmin.url_helper.get_action_url('inspect', result.pk)

        return HttpResponseRedirect(result_url)
