from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from payments.models import ExternalApp


class APIKeyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        api_key = request.headers.get("X-API-KEY")

        if not api_key:
            return None

        try:
            app = ExternalApp.objects.get(api_key=api_key, is_active=True)
        except ExternalApp.DoesNotExist:
            raise AuthenticationFailed("Invalid API Key")

        return (app, None)
