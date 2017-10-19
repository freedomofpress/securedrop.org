from landing_page_checker.models import SecuredropPage
from django.views.generic import ListView, DetailView

class SecuredropList(ListView):
    model = SecuredropPage

class SecuredropDetail(DetailView):
    model = SecuredropPage
