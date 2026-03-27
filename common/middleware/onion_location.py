from django.conf import settings


class OnionLocationHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Onion-Location'] = f'http://{settings.ONION_HOSTNAME}{request.get_full_path()}'
        return response
