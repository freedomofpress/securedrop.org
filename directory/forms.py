from django import forms


class DirectoryForm(forms.Form):
    organization = forms.CharField(label="Organization", max_length=255)
    url = forms.URLField()
    tor_address = forms.CharField(label="Tor address", max_length=255)
