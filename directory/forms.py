from django import forms


class ScannerForm(forms.Form):
    error_css_class = 'basic-form__error'
    required_css_class = 'basic-form__required'

    url = forms.URLField()


class ManualScanForm(forms.Form):
    landing_page_url = forms.URLField(required=True)
    permitted_domains = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 20}),
        help_text=('Optional comma-separated list of additional domains that will not trigger '
                   'the cross domain asset warning for this landing page.  '
                   'Subdomains on domains in this list are ignored.  For example, '
                   'adding "news.bbc.co.uk" permits all assets from "bbc.co.uk".'),
    )
