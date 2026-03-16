from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.utils import get_md5_hash_password
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import Token
from rest_framework.renderers import BaseRenderer

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from utils import serializer_encoder
from .models import BdayaUser

class GraphQLAuthMiddleware:

    def resolve(self, next, root, info, **kwargs):
        request = info.context
        if request.user.is_authenticated:
            return next(root, info, **kwargs)
        
        try:
            token_auth = CookiesJWTAuthentication()
            user_token_auth = token_auth.authenticate(request)
            
            if user_token_auth:
                info.context.user = user_token_auth[0]
            else:
                info.context.user = AnonymousUser()
        except AuthenticationFailed:
            info.context.user = AnonymousUser()
        
        return next(root, info, **kwargs)


class CookiesJWTAuthentication(JWTAuthentication):
    def authenticate(self, request) -> None | tuple[BdayaUser, Token]:
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get('access_token')
            
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except:
            return None
        
    def get_user(self, validated_token: Token) -> BdayaUser:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM] # type: ignore
        except KeyError as e:
            raise InvalidToken(
                _("Token contained no recognizable user identification")
            ) from e

        try:
            user = (
                self.user_model.objects
                .only("id", "email", "password", "username", "role", "is_active", "is_superuser", "track_id", "track__name")
                .select_related("track")
                .get(**{api_settings.USER_ID_FIELD: user_id}) # type: ignore
            )
        except self.user_model.DoesNotExist as e:
            raise AuthenticationFailed(
                _("User not found"), code="user_not_found"
            ) from e

        if api_settings.CHECK_USER_IS_ACTIVE and not user.is_active:
            raise AuthenticationFailed(_("User is inactive"), code="user_inactive")

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(
                api_settings.REVOKE_TOKEN_CLAIM # type: ignore
            ) != get_md5_hash_password(user.password):
                raise AuthenticationFailed(
                    _("The user's password has been changed."), code="password_changed"
                )

        return user


class RawJsonRenderer(BaseRenderer):
    media_type = "application/json"
    format = 'json'
    
    def render(self, data, accepted_media_type=None, renderer_context=None) -> bytes:
        if isinstance(data, bytes):
            return data
            
        return serializer_encoder.encode(data)