from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from django_bolt import Middleware, Request
from asgiref.sync import async_to_sync
from django.http import SimpleCookie
from django.conf import settings
from .models import BdayaUser
from utils import STORE
from typing import Any
import tracemalloc
import time
import jwt

async def get_user_from_token(raw_token: str) -> BdayaUser | AnonymousUser:
    """
    Universal async authenticator. Replaces CookiesJWTAuthentication.
    """
    if not raw_token:
        return AnonymousUser()
        
    try:
        payload = jwt.decode(
            raw_token, 
            settings.SECRET_KEY, 
            algorithms=['HS256'],
        )
        
        if payload.get("token_type") != "access":
            return AnonymousUser()
        
        jti = payload.get("jti")
        if jti and await STORE.is_revoked(jti):
            return AnonymousUser()

        user_id = payload.get('sub')
        if not user_id:
            return AnonymousUser()

        user = await (
            BdayaUser.objects
            .defer("track__prefix", "is_staff", "joined_at", "last_login", "track__en_description", "track__ar_description", "track__image","member__joined_at", "member__status")
            .select_related("track", 'member')
            .aget(id=user_id)
        )

        if not user.is_active:
            return AnonymousUser()

        return user

    except (jwt.PyJWTError, BdayaUser.DoesNotExist):
        return AnonymousUser()


class GraphQLAuthMiddleware:

    def resolve(self, next, root, info, **kwargs):
        request = info.context
        if request.user.is_authenticated:
            return next(root, info, **kwargs)
        
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                raw_token = auth_header.split(' ')[1]
        
        if raw_token:
            user = async_to_sync(get_user_from_token)(raw_token)
            info.context.user = user
        else:
            info.context.user = AnonymousUser()
        
        return next(root, info, **kwargs)


class JWTSocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send): # type: ignore
        headers = dict(scope.get('headers', []))
        scope['user'] = AnonymousUser()  # type: ignore
        
        if cookies:= (headers.get(b'cookie') or headers.get(b'Cookie')):
            cookie_str = cookies.decode()
            cookie_parser = SimpleCookie(cookie_str)
            
            token = cookie_parser.get('access_token')
            if token:
                scope['user'] = await get_user_from_token(token.value) # type: ignore
        
        if scope['user'].is_anonymous:
            await send({
                "type": "websocket.close",
                "code": 4001
            }) # type: ignore
            return
        
        return await super().__call__(scope, receive, send)

class TrackMemoryLeakMiddleware(Middleware):
    async def process_request(self, request: Request) -> Any:
        tracemalloc.start()
        response = await self.get_response(request)
        snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        top_status = snapshot.statistics('lineno')
        print("\nMemory Leaks")
        for status in top_status[:5]:
            print(status)
        print()
        return response

class TrackTimeMiddleware(Middleware):
    async def process_request(self, request: Request) -> Any:
        start = time.perf_counter()
        response = await self.get_response(request)
        total = round(time.perf_counter() - start, 4)
        print(f"\nAsync Finished at {total}\n")
        response.headers['X-Time'] = f"{total}ms"
        return response