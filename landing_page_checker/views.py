from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from directory.forms import LandingPageForm
from landing_page_checker.landing_page.scanner import scan, clean_url
from landing_page_checker.models import Securedrop


class SecuredropListView(ListView):
    model = Securedrop
    template_name = 'home.html'


class SecuredropDetailView(DetailView):
    model = Securedrop
    template_name = 'securedrop_detail.html'


def landing_page_test(request):
    form = LandingPageForm()
    return render(request, 'landing_page_test.html', {'form': form})


def scan_landing_page(request):
    url = request.POST['url']
    form = LandingPageForm({'url': url})
    if request.method == 'POST' and form.is_valid():
        securedrop = Securedrop(organization='Unknown',
                                landing_page_domain=clean_url(url),
                                onion_address='Unknown')
        scan_result = scan(securedrop)
        scan_result.compute_grade()
        return render(request, 'result.html', {'result': scan_result, 'url': url})
    else:
        return redirect('landing_page_test')
