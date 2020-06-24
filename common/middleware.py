from common.models import FooterSettings


class OnionLocationMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        footer_settings = FooterSettings.for_site(request.site)
        if footer_settings.securedrop_onion_address:
            response['Onion-Location'] = footer_settings.securedrop_onion_address
        return response
