from django import forms
from captcha.fields import ReCaptchaField
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _


from autocomplete.widgets import Autocomplete
from directory.models import Language, Topic, Country
from landing_page_checker.models import SecuredropPage


class DirectoryForm(forms.ModelForm):
    title = forms.CharField(label=_("Organization name"), max_length=255)
    onion_address = forms.CharField(
        label="Tor address",
        max_length=255,
        validators=[RegexValidator(regex=r'\.onion$', message=_("Enter a valid .onion address"))],
    )
    organization_logo = forms.FileField(required=False)
    languages_accepted = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        widget=type(
            '_Autocomplete',
            (Autocomplete,),
            dict(page_type='directory.Language', can_create=True, is_single=False, api_base='/autocomplete/')
        ),
        required=False
    )
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=type(
            '_Autocomplete',
            (Autocomplete,),
            dict(page_type='directory.Topic', can_create=True, is_single=False, api_base='/autocomplete/')
        ),
        required=False
    )
    countries = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(),
        widget=type(
            '_Autocomplete',
            (Autocomplete,),
            dict(page_type='directory.Country', can_create=True, is_single=False, api_base='/autocomplete/')
        ),
        required=False
    )

    class Meta:
        model = SecuredropPage
        fields = ['landing_page_domain', 'organization_description']


class ScannerForm(forms.Form):
    url = forms.URLField()
    captcha = ReCaptchaField(label='')
