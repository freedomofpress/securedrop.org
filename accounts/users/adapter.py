from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter
from wagtail.wagtailcore.models import Site

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        path = reverse('dashboard')
        return path

    def format_email_subject(self, subject):
        site = Site.objects.get(is_default_site=True)
        prefix = "[{name}] ".format(name=site.site_name)
        return prefix + force_text(subject)
