from landing_page_checker.models import SecuredropPage
from django.views.generic import ListView, DetailView
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
class SecuredropDetail(DetailView):
    model = SecuredropPage

    def get_object(self, **kwargs):
        obj = super(SecuredropDetail, self).get_object(**kwargs)
        if self.request.user not in [ o.owner for o in obj.owners.all() ]:
            raise PermissionDenied
        return obj
