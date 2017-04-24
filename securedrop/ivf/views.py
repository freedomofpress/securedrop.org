from django.shortcuts import redirect, render

from ivf.forms import LandingPageForm
from ivf.utils import get_results


def home_page(request):
    form = LandingPageForm()
    return render(request, 'home.html', {'form': form})


def scan_landing_page(request):
    url = request.POST['url']
    form = LandingPageForm({'url': url})
    if request.method == 'POST' and form.is_valid():
        results = get_results(url)
        return render(request, 'result.html', {'results': results, 'url': url})
    else:
        return redirect('ivf.views.home_page')
