from django import forms
from captcha.fields import ReCaptchaField


class DirectoryForm(forms.Form):
    organization = forms.CharField(label="Organization", max_length=255)
    url = forms.URLField()
    tor_address = forms.CharField(label="Tor address", max_length=255)


class ScannerForm(forms.Form):
    url = forms.URLField()
    captcha = ReCaptchaField(label='')
