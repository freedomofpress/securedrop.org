from landing_page_checker.models import SecuredropPage
from django.views.generic import ListView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


@method_decorator(login_required, name='dispatch')
class SecuredropList(ListView):
    model = SecuredropPage

    def get_queryset(self, **kwargs):
        queryset = super(SecuredropList, self).get_queryset(**kwargs)
        print(self.request.user)
        return queryset.filter(owners__owner=self.request.user)


@method_decorator(login_required, name='dispatch')
class SecuredropDetail(UpdateView):
    model = SecuredropPage

    fields = ['title', 'landing_page_domain', 'onion_address', 'organization_description', 'organization_logo']

    def get_success_url(self):
        return self.object.url

    def get_object(self, **kwargs):
        obj = super(SecuredropDetail, self).get_object(**kwargs)
        if self.request.user not in [ o.owner for o in obj.owners.all() ]:
            raise PermissionDenied
        return obj

