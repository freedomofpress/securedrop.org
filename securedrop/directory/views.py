from django.shortcuts import redirect, render

from directory.forms import LandingPageForm
from directory.utils import LandingPage


def home_page(request):
    form = LandingPageForm()
    return render(request, 'home.html', {'form': form})


def scan_landing_page(request):
    url = request.POST['url']
    form = LandingPageForm({'url': url})
    if request.method == 'POST' and form.is_valid():
        page = LandingPage(url)
        results, grade = page.get_results()
        return render(request, 'result.html', {'results': results, 'url': url,
                                               'grade': grade})
    else:
        return redirect('directory.views.home_page')
