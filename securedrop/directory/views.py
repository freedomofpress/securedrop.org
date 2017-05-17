from django.shortcuts import redirect, render
from django.views.generic.list import ListView

from directory.forms import LandingPageForm
from directory.models import Securedrop
from directory.utils import LandingPage


class SecuredropListView(ListView):
    model = Securedrop
    template_name = 'home.html'


def landing_page_test(request):
    form = LandingPageForm()
    return render(request, 'landing_page_test.html', {'form': form})


def scan_landing_page(request):
    url = request.POST['url']
    form = LandingPageForm({'url': url})
    if request.method == 'POST' and form.is_valid():
        page = LandingPage(url)
        results, grade = page.get_results()
        return render(request, 'result.html', {'results': results, 'url': url,
                                               'grade': grade})
    else:
        return redirect('landing_page_test')
