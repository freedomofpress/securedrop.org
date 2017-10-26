from landing_page_checker.models import SecuredropPage, SecuredropOwner
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple, RelatedFieldWidgetWrapper
from django.db.models.fields.related import ManyToManyRel
from modelcluster.forms import ClusterForm
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from wagtail.wagtailimages import get_image_model

User = get_user_model()
WagtailImage = get_image_model()


class SignupForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


class SecuredropPageForm(forms.ModelForm):
    add_owner = forms.EmailField(required=False)
    organization_logo = forms.FileField(required=False)

    def __init__(self, user=None, *args, **kwargs):
        self.fields['owners'].queryset = self.instance.owners.all()

    def clean(self):
        cleaned_data = super(SecuredropPageForm, self).clean()

        if cleaned_data['add_owner']:
            try:
                new_owner = cleaned_data['add_owner']
                User.objects.get(email=new_owner)
            except ObjectDoesNotExist:
                msg = ValidationError("That user does not exist", code='invalid')
                self.add_error("add_owner", msg)

        if cleaned_data['organization_logo']:
            try:
                img_title = cleaned_data['title'] + "logo"
                img = WagtailImage.objects.create(title=img_title, file=cleaned_data['organization_logo'])
                cleaned_data['organization_logo'] = img
            except:
                msg = ValidationError("That image could not be saved", code='invalid')
                self.add_error("organization_logo", msg)

        return cleaned_data

    def save(self, commit=True):
        # Get the unsave Pizza instance
        instance = forms.ModelForm.save(self, False)
        # Add owner to the form
        if self.cleaned_data['add_owner']:
            new_owner = User.objects.get(email=self.cleaned_data['add_owner'])
            sdo = SecuredropOwner.objects.create(owner=new_owner, page=instance)
        else:
            sdo = None

        if self.cleaned_data['organization_logo']:
            pass


        # Do we need to save all changes now?
        if commit:
            if self.cleaned_data['organization_logo']:
                self.cleaned_data['organization_logo'].save()
                instance.organization_logo = self.cleaned_data['organization_logo']
            instance.save()
            self.save_m2m()
            if sdo:
                sdo.save()
            if self.cleaned_data['organization_logo']:
                self.cleaned_data['organization_logo'].save()
                instance.organization_logo = self.cleaned_data['organization_logo']

        return instance

    class Meta:
        model = SecuredropPage
        fields = ['title', 'landing_page_domain', 'onion_address', 'organization_description',]
