from django import forms
from django.contrib.auth import get_user_model


class SignupForm(forms.ModelForm):
    error_css_class = 'basic-form__error'
    required_css_class = 'basic-form__required'

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
