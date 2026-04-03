from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.utils import get_md5_hash_password
from rest_framework_simplejwt.tokens import Token, AccessToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework.exceptions import AuthenticationFailed

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from django.http import SimpleCookie
from django.core.cache import cache

from utils import serializer_encoder
from .models import BdayaUser

from ninja.renderers import BaseRenderer as NinjaBaseRenderer
from ninja_extra.security import AsyncAPIKeyCookie

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
                .defer("track__prefix", "is_staff", "joined_at", "last_login", "track__en_description", "track__ar_description", "track__image","member__joined_at", "member__status",)
                .select_related("track", 'member')
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
    
class AsyncCookiesJWTAuth(AsyncAPIKeyCookie):
    param_name = "access_token"

    # You MUST name this method "authenticate" to satisfy the Abstract Base Class
    async def authenticate(self, request, key):
        
        if not key:
            header = request.headers.get("Authorization")
            if header and header.startswith("Bearer"):
                key = header.split(" ")[1]

        if not key:
            return None

        try:
            validated_token = AccessToken(key) # type: ignore
            user_id = validated_token[api_settings.USER_ID_CLAIM] # type: ignore
        except (TokenError, KeyError) as e:
            return None
        
        # 3. Check Redis Cache
        cache_key = f"auth_user_{user_id}"
        user = await cache.aget(cache_key)
        
        # 4. Database Query (if not in cache)
        if not user:
            try:
                user = await (
                    BdayaUser.objects
                    .defer("track__prefix", "is_staff", "joined_at", "last_login", "track__en_description", "track__ar_description", "track__image", "member__joined_at", "member__status")
                    .select_related("track", "member")
                    .aget(**{api_settings.USER_ID_FIELD: user_id}) # type: ignore
                )
            except BdayaUser.DoesNotExist:
                return None

            # Security Checks
            if api_settings.CHECK_USER_IS_ACTIVE and not user.is_active:
                return None

            if api_settings.CHECK_REVOKE_TOKEN:
                if validated_token.get(api_settings.REVOKE_TOKEN_CLAIM) != get_md5_hash_password(user.password): # type: ignore
                    return None
            
            await cache.aset(cache_key, user, 3600)

        request.user = user
        return user

@database_sync_to_async
def get_user_from_socket(token) -> BdayaUser | AnonymousUser:
    auth = CookiesJWTAuthentication()
    
    try:
        token = auth.get_validated_token(token)
        user = auth.get_user(token)
        return user
    except:
        return AnonymousUser()

class JWTSocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send): # type: ignore
        headers = dict(scope.get('headers', []))
        scope['user'] = AnonymousUser()  # type: ignore
        
        if headers.get(b'cookie'):
            cookie_str = headers[b'cookie'].decode()
            cookie_parser = SimpleCookie(cookie_str)
            
            token = cookie_parser.get('access_token')
            if token:
                scope['user'] = await get_user_from_socket(token.value) # type: ignore
        
        if scope['user'].is_anonymous:
            await send({
                "type": "websocket.close",
                "code": 4001
            }) # type: ignore
            return
        
        return await super().__call__(scope, receive, send)


class RawJsonMSGRenderer(NinjaBaseRenderer):
    media_type = "application/json"
    
    def render(self, request, data, *, response_status) -> bytes:
        if isinstance(data, bytes):
            return data
            
        return serializer_encoder.encode(data)
    