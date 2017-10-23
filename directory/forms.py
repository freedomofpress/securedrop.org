from django import forms
from captcha.fields import ReCaptchaField

from wagtail.wagtailimages.widgets import AdminImageChooser
from autocomplete.widgets import Autocomplete
from directory.models import Language
from common.models import CustomImage


class DirectoryForm(forms.Form):
    organization = forms.CharField(label="Organization", max_length=255)
    url = forms.URLField()
    tor_address = forms.CharField(label="Tor address", max_length=255)
    languages_accepted = forms.ModelMultipleChoiceField(queryset=Language.objects.all(), widget=type(
                '_Autocomplete',
                (Autocomplete,),
                dict(page_type='directory.Language', can_create=True, is_single=False, api_base='/autocomplete/')
            ))


class ScannerForm(forms.Form):
    url = forms.URLField()
    captcha = ReCaptchaField(label='')
