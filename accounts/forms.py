from landing_page_checker.models import SecuredropPage, SecuredropOwner
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple, RelatedFieldWidgetWrapper
from django.db.models.fields.related import ManyToManyRel
from modelcluster.forms import ClusterForm
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError

User = get_user_model()

class SignupForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name']

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()


class SecuredropPageForm(forms.ModelForm):
    add_owner = forms.EmailField()


    # def __init__(self, *args, **kwargs):
    #     if kwargs.get('instance'):
    #         initial = kwargs.setdefault('initial', {})
    #         initial['owners'] = [owner.owner for owner in kwargs['instance'].owners.all()]


    def clean(self):
        cleaned_data = super(SecuredropPageForm, self).clean()
        try:
            User.objects.get(email=cleaned_data['add_owner'])
        except ObjectDoesNotExist:
            msg = ValidationError("That user does not exist", code='invalid')
            self.add_error("add_owner", msg)

    def save(self, commit=True):
        # Get the unsave Pizza instance
        instance = forms.ModelForm.save(self, False)
        print(self.cleaned_data)
        # Add owner to the form
        new_owner = User.objects.get(email=self.cleaned_data['add_owner'])
        sdo = SecuredropOwner.objects.create(owner=new_owner, page=instance)

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()
            sdo.save()

        return instance

    class Meta:
        model = SecuredropPage
        fields = ['title', 'landing_page_domain', 'onion_address', 'organization_description', 'organization_logo',]
