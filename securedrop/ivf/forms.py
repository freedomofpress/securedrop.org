from django.core.exceptions import ValidationError
from django import forms


class LandingPageForm(forms.Form):
    url = forms.URLField(required=True, min_length=5, label='URL')
    url.widget.attrs.update({'class' : 'form-control input-lg'})
