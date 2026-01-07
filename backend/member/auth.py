from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.request import Request


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
