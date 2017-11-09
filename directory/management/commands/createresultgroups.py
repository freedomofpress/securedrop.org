from django.db import transaction
from django.core.management.base import BaseCommand

from wagtail.wagtailcore.rich_text import RichText

from directory.models import ResultGroup, ResultState


class Command(BaseCommand):
    help = 'Creates result groups that store information shown as scan results.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete all result groups and create new ones',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['delete']:
            ResultGroup.objects.all().delete()
            ResultState.objects.all().delete()

        basic, _ = ResultGroup.objects.get_or_create(name='Basic')
        https, _ = ResultGroup.objects.get_or_create(name='HTTPS')
        server_security, _ = ResultGroup.objects.get_or_create(name='Server Security')
        caching, _ = ResultGroup.objects.get_or_create(name='Caching')
        metadata, _ = ResultGroup.objects.get_or_create(name='Metadata')
        third_parties, _ = ResultGroup.objects.get_or_create(name='3rd Parties')
        local_storage, _ = ResultGroup.objects.get_or_create(name='Local Storage')

        ResultState.objects.bulk_create([
            ResultState(
                name='live',
                success_text='Successfully received landing page.',
                failure_text='Could not get to landing page.',
                is_warning=False,
                result_group=basic,
                sort_order=1
            ),
            ResultState(
                name='http_status_200_ok',
                success_text='Server responded with 200 OK.',
                failure_text='Server did not respond with 200 OK.',
                is_warning=False,
                result_group=basic,
                sort_order=2
            ),
            ResultState(
                name='http_no_redirect',
                success_text='Landing page does not redirect.',
                failure_text='Landing page should not redirect.',
                is_warning=False,
                result_group=basic,
                sort_order=3
            ),
            ResultState(
                name='expected_encoding',
                success_text='Expected encoding found on landing page.',
                failure_text='Unexpected encoding found on landing page.',
                is_warning=False,
                result_group=basic,
                sort_order=4
            ),
            ResultState(
                name='forces_https',
                success_text='Landing page enforces HTTPS.',
                failure_text='Landing page does not enforce HTTPS. HTTPS is critical for security on the landing page.',
                fix_text=RichText("<a href='https://securethe.news/why/'>Why?</a><a  href='https://securethe.news/how/'>How can I set up HTTPS?</a>"),
                is_warning=False,
                result_group=https,
                sort_order=1
            ),
            ResultState(
                name='hsts',
                success_text='HSTS is supported.',
                failure_text='HSTS is not supported.',
                is_warning=True,
                result_group=https,
                sort_order=2
            ),
            ResultState(
                name='hsts_max_age',
                success_text='HSTS max age is at least a year.',
                failure_text='HSTS max age is less than a year.',
                is_warning=True,
                result_group=https,
                sort_order=3
            ),
            ResultState(
                name='hsts_entire_domain',
                success_text='HTTPS is enforced on the entire domain.',
                failure_text='HTTPS is not enforced on the entire domain.',
                is_warning=True,
                result_group=https,
                sort_order=4
            ),
            ResultState(
                name='hsts_preloaded',
                success_text='HSTS preloaded',
                failure_text=RichText('The page is not <a href="https://hstspreload.org/">HSTS preloaded</a>'),
                is_warning=True,
                result_group=https,
                sort_order=5
            ),
            ResultState(
                name='no_server_info',
                success_text='Server software not found in headers.',
                failure_text='Server software should not appear in headers.',
                is_warning=True,
                result_group=server_security,
                sort_order=1
            ),
            ResultState(
                name='no_server_version',
                success_text='No version info found in headers.',
                failure_text='Software version should not appear in headers.',
                is_warning=True,
                result_group=server_security,
                sort_order=2
            ),
            ResultState(
                name='csp_origin_only',
                success_text='HSTS preloaded',
                failure_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP">Content Security Policy (CSP)</a> loads only from the origin domain.'),
                fix_text=RichText("<p>Add the following to your security headers:</p><pre>Content-Security-Policy default-src 'self'</pre>"),
                is_warning=True,
                result_group=server_security,
                sort_order=3
            ),
            ResultState(
                name='mime_sniffing_blocked',
                success_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options">MIME sniffing</a> is blocked.'),
                failure_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options">MIME sniffing</a> is possible.'),
                is_warning=True,
                result_group=server_security,
                sort_order=4
            ),
            ResultState(
                name='noopen_download',
                success_text=RichText('Users cannot accidentally <a href="https://msdn.microsoft.com/en-us/library/jj542450(v=vs.85).aspx">open a download</a>'),
                failure_text=RichText('Users can accidentally <a href="https://msdn.microsoft.com/en-us/library/jj542450(v=vs.85).aspx">open a download</a>'),
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>X-Download-Options noopen</pre>'),
                is_warning=True,
                result_group=server_security,
                sort_order=5
            ),
            ResultState(
                name='xss_protection',
                success_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection">XSS filtering</a> is enabled.'),
                failure_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection">XSS attacks</a> are not prevented.'),
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>X-XSS-Protection 1; mode=block</pre>'),
                is_warning=True,
                result_group=server_security,
                sort_order=6
            ),
            ResultState(
                name='clickjacking_protection',
                success_text=RichText('Ensures that the server forbids embedding this page within an iframe, to <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options">prevent clickjacking attacks</a>. Otherwise another site could embed the Landing Page and mess with it.'),
                failure_text=RichText('The server does not forbid embedding this page within an iframe, to <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options">prevent clickjacking attacks</a>. Another site could embed the Landing Page and mess with it.'),
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>X-Frame-Options DENY</pre>'),
                is_warning=True,
                result_group=server_security,
                sort_order=7
            ),
            ResultState(
                name='good_cross_domain_policy',
                success_text='Cross Domain Policy set correctly.',
                failure_text='Cross Domain Policy not set correctly.',
                is_warning=True,
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>X-Permitted-Cross-Domain-Policies master-only</pre>'),
                result_group=server_security,
                sort_order=8
            ),
            ResultState(
                name='http_1_0_caching_disabled',
                success_text='Caching is disabled (HTTP/1.0).',
                failure_text='Caching is not disabled (HTTP/1.0).',
                is_warning=True,
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>Pragma no-cache</pre>'),
                result_group=caching,
                sort_order=1
            ),
            ResultState(
                name='cache_control_set',
                success_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Caching</a> is disabled (HTTP/1.1).'),
                failure_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Caching</a> is not disabled (HTTP/1.1).'),
                is_warning=True,
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>Cache-Control "max-age=0, no-cache, no-store, must-revalidate, private"</pre>'),
                result_group=caching,
                sort_order=2
            ),
            ResultState(
                name='cache_control_revalidate_set',
                success_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Cache-Control</a> must revalidate header set properly.'),
                failure_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Cache-Control</a> must-revalidate header not set properly.'),
                is_warning=True,
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>Cache-Control "max-age=0, no-cache, no-store, must-revalidate, private"</pre>'),
                result_group=caching,
                sort_order=3
            ),
            ResultState(
                name='cache_control_nocache_set',
                success_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Cache-Control</a> no-cache header set properly.'),
                failure_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Cache-Control</a> no-cache header not set properly.'),
                is_warning=True,
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>Cache-Control "max-age=0, no-cache, no-store, must-revalidate, private"</pre>'),
                result_group=caching,
                sort_order=4
            ),
            ResultState(
                name='cache_control_notransform_set',
                success_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Cache-Control</a> no-store header set properly.'),
                failure_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Cache-Control</a> no-store header not set properly.'),
                is_warning=True,
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>Cache-Control "max-age=0, no-cache, no-store, must-revalidate, private"</pre>'),
                result_group=caching,
                sort_order=5
            ),
            ResultState(
                name='cache_control_private_set',
                success_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Cache-Control</a> private header set properly.'),
                failure_text=RichText('<a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control">Cache-Control</a> private header not set properly.'),
                is_warning=True,
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>Cache-Control "max-age=0, no-cache, no-store, must-revalidate, private"</pre>'),
                result_group=caching,
                sort_order=6
            ),
            ResultState(
                name='expires_set',
                success_text=RichText('The page is <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Expires">marked as expired</a>, so no cache will be used.'),
                failure_text=RichText('The page is not <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Expires">marked as expired</a>. Cache may be used.'),
                is_warning=True,
                fix_text=RichText('<p>Add the following to your security headers:</p><pre>Expires -1</pre>'),
                result_group=caching,
                sort_order=7
            ),
            ResultState(
                name='safe_onion_address',
                success_text='No clickable onion addresses were found.',
                failure_text='Onion address should not be a clickable link. If clicked, some browsers will send a DNS request that will not be routed through tor, producing metadata that can identify a source.',
                is_warning=False,
                result_group=metadata,
                sort_order=1
            ),
            ResultState(
                name='subdomain',
                success_text='Landing page is not hosted on a subdomain.',
                failure_text='Landing page should not be hosted on a subdomain. Using a subdomain can reveal to a passive observer that the client is looking at the securedrop page on your website.',
                is_warning=True,
                result_group=metadata,
                sort_order=2
            ),
            ResultState(
                name='no_cdn',
                success_text='Use of CDNs not found.',
                failure_text='CDNs are a 3rd party that function by man-in-the-middling traffic. Do not use a CDN on the landing page.',
                is_warning=True,
                result_group=third_parties,
                sort_order=1
            ),
            ResultState(
                name='no_analytics',
                success_text='Use of Google Analytics not found.',
                failure_text='Google Analytics provides information that can be stored and disclosed by 3rd parties. Do not use analytics on the landing page.',
                is_warning=False,
                result_group=third_parties,
                sort_order=2
            ),
            ResultState(
                name='no_cookies',
                success_text='Landing page does not use cookies.',
                failure_text='The landing page should not use cookies.',
                is_warning=False,
                result_group=local_storage,
                sort_order=1
            ),
        ])
