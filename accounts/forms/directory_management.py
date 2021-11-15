from directory.models import SecuredropOwner, DirectoryEntry
from django.contrib.auth import get_user_model
from django import forms
from django.core.exceptions import ValidationError
from wagtail.images import get_image_model
from django.utils.translation import ugettext_lazy as _

from wagtailautocomplete.widgets import Autocomplete
from directory.models.taxonomy import Language, Topic, Country


class LandingPageForm(forms.Form):
    url = forms.URLField(required=True, min_length=5, label='URL')
    url.widget.attrs.update({
        'class': 'form-control input-lg',
        'placeholder': 'https://example.com/securedrop'
    })


class DirectoryEntryForm(forms.ModelForm):
    error_css_class = 'basic-form__error'
    required_css_class = 'basic-form__required'

    organization_logo = forms.FileField(required=False)

    def __init__(self, directory_page, user=None, *args, **kwargs):
        super(DirectoryEntryForm, self).__init__(*args, **kwargs)

        self.directory_page = directory_page
        self.user = user

    def clean_title(self):
        data = self.cleaned_data['title']

        pages = DirectoryEntry.objects.filter(title=data)
        if self.instance.pk:
            pages = pages.exclude(pk=self.instance.pk)

        if pages.exists():
            raise ValidationError('Securedrop page with this Organization name already exists.')

        return data

    def clean_organization_logo(self):
        WagtailImage = get_image_model()
        organization_logo_file = self.cleaned_data['organization_logo']

        if organization_logo_file == self.instance.organization_logo_id:
            return self.instance.organization_logo

        if not organization_logo_file:
            return None

        try:
            organization_logo = WagtailImage.objects.create(
                title='{} logo'.format(self.cleaned_data['title']),
                file=organization_logo_file,
            )
        except Exception:
            raise ValidationError('That image could not be saved')

        return organization_logo

    def save(self, commit=True):
        # Get the unsaved instance
        instance = super(DirectoryEntryForm, self).save(commit=False)

        instance.live = False

        if commit:
            if not instance.pk:
                self.directory_page.add_child(instance=instance)

            instance.save()
            self.save_m2m()

            # Editing user is always an owner
            if self.user:
                SecuredropOwner.objects.get_or_create(
                    owner=self.user,
                    page=instance,
                )

        return instance

    class Meta:
        model = DirectoryEntry
        fields = [
            'title',
            'landing_page_url',
            'organization_description',
            'onion_address',
            'organization_logo',
            'languages',
            'topics',
            'countries',
        ]
        labels = {
            'onion_address': _('Tor address'),
            'title': _('Organization name')
        }
        widgets = {
            'languages': Autocomplete(
                target_model=Language,
                can_create=True,
                is_single=False
            ),
            'topics': Autocomplete(
                target_model=Topic,
                can_create=True,
                is_single=False
            ),
            'countries': Autocomplete(
                target_model=Country,
                can_create=True,
                is_single=False
            ),
        }


class DirectoryEntryOwnerForm(DirectoryEntryForm):
    add_owner = forms.EmailField(required=False)
    remove_owners = forms.ModelMultipleChoiceField(queryset=SecuredropOwner.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        super(DirectoryEntryOwnerForm, self).__init__(*args, **kwargs)

        owners_qs = self.instance.owners.all()
        if self.user:
            owners_qs = owners_qs.exclude(owner=self.user)

        if owners_qs:
            self.fields['remove_owners'].queryset = owners_qs
        else:
            del self.fields['remove_owners']

    def clean_add_owner(self):
        User = get_user_model()
        add_owner_email = self.cleaned_data['add_owner']

        if not add_owner_email:
            return None

        try:
            add_owner = User.objects.get(email=add_owner_email)
        except User.DoesNotExist:
            raise ValidationError(_("That user does not exist"), code='invalid')
        return add_owner

    def save(self, commit=True):
        instance = super(DirectoryEntryOwnerForm, self).save(commit)

        if commit:
            if self.cleaned_data.get('remove_owners'):
                self.cleaned_data['remove_owners'].delete()

            # Add owner
            new_owner = self.cleaned_data.get('add_owner')
            if new_owner:
                SecuredropOwner.objects.create(
                    owner=new_owner,
                    page=instance,
                )

        return instance

    class Meta(DirectoryEntryForm.Meta):
        fields = [
            'title',
            'landing_page_url',
            'organization_description',
            'onion_address',
            'add_owner',
            'remove_owners',
            'organization_logo',
            'languages',
            'topics',
            'countries',
        ]
