from captcha.fields import ReCaptchaField
from django import forms


class ScannerForm(forms.Form):
    error_css_class = 'basic-form__error'
    required_css_class = 'basic-form__required'

    url = forms.URLField()
    captcha = ReCaptchaField(label='')
