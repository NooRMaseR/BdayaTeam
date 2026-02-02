from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.renderers import BaseRenderer
from rest_framework.request import Request
from utils import serializer_encoder


class CookieTokenAuthentication(BaseAuthentication):
    """
    Authenticates using DRF Token stored in HttpOnly cookie
    """

    def authenticate(self, request: Request):
        token_key: str | None = request.COOKIES.get("auth_token")
        
        if not token_key:
            return None

        try:
            token = Token.objects.select_related("user").get(key=token_key)
        except Token.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        if not token.user.is_active:
            raise AuthenticationFailed("User inactive")

        return (token.user, token)

class RawJsonRenderer(BaseRenderer):
    media_type = "application/json"
    format = 'json'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, bytes):
            return data
        elif data is not None:
            return serializer_encoder.encode(data)
        else:
            return data