from django.urls import reverse
from wagtail.wagtailcore.models import Site
from django_otp import user_has_device
from allauth_2fa.adapter import OTPAdapter
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text


class MyAccountAdapter(OTPAdapter):
    def get_login_redirect_url(self, request):
        # This ensures that once a user registers, they immediately
        # find the 2FA setup page after login.
        if not user_has_device(request.user):
            path = reverse('two-factor-setup')

        # request.user.otp_device will be None if the user is not
        # verified.  I am not sure why at this point in the request
        # cycle the `is_verified` function (which uses this same
        # logic) has not been added to the user object.
        elif request.user.is_authenticated and request.user.otp_device is None:
            # The session key here seems required to let allauth_2fa
            # know to bypass normal login and request a token.
            request.session['allauth_2fa_user_id'] = request.user.id
            path = reverse('two-factor-authenticate')
        else:
            path = reverse('dashboard')
        return path

    def format_email_subject(self, subject):
        site = Site.objects.get(is_default_site=True)
        prefix = "[{name}] ".format(name=site.site_name)
        return prefix + force_text(subject)
