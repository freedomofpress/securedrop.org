from captcha.fields import ReCaptchaField
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


from autocomplete.widgets import Autocomplete
from directory.models import Language, Topic, Country
from landing_page_checker.models import SecuredropPage


class DirectoryForm(forms.ModelForm):
    error_css_class = 'basic-form__error'
    required_css_class = 'basic-form__required'

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

    def clean_title(self):
        data = self.cleaned_data['title']
        if SecuredropPage.objects.filter(title=data).exists():
            raise ValidationError('Securedrop page with this Organization name already exists.')
        return data

    class Meta:
        model = SecuredropPage
        fields = [
            'landing_page_domain',
            'organization_description',
            'title',
            'onion_address',
        ]
        labels = {
            'onion_address': _('Tor address'),
            'title': _('Organization name')
        }


class ScannerForm(forms.Form):
    error_css_class = 'basic-form__error'
    required_css_class = 'basic-form__required'

    url = forms.URLField()
    captcha = ReCaptchaField(label='')
