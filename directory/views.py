from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.urls import reverse

from scanner.scanner import perform_scan

from .forms import ManualScanForm


class ManualScanView(FormView):
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

        scanresult_viewset = ScanResultAdmin()

        permitted_domains = form.cleaned_data['permitted_domains'].split(',')
        landing_page_url = form.cleaned_data['landing_page_url']

        result = perform_scan(landing_page_url, permitted_domains)
        result.save()

        result_url = reverse(scanresult_viewset.get_url_name('inspect'), kwargs={'pk': result.pk})

        return HttpResponseRedirect(result_url)
