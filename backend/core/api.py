from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from member.api import MemberEditTaskController, MemberProfileController, ProtectedTaskController, TasksController
from member.models import Member

from organizer.api import AttendanceDaysConrtoller, MembersController, SettingsController
from organizer.serializers import SiteSettingsImagesMSGSerializer
from organizer.models import SiteSetting

from technical.api import TechnicalMembersController, TechnicalTasksController

from .middleware import AsyncCookiesJWTAuth, AsyncSafeThrottle, RawJsonMSGRenderer
from .models import BdayaUser, PushSubscription, Track, TrackCounter, UserRole
from .serializers import TrackMSGSerializer, TrackNameOnlyMSGSerializer
from .permissions import NinjaIsOrganizer, NinjaIsSuperUser
from .caches import TRACKS_CACHE_KEY, track_cache_key
from .tasks import send_member_email
from . import api_schemas

from django.shortcuts import get_object_or_404, aget_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse
from django.core.cache import cache
from django.middleware import csrf
from django.conf import settings
from django.contrib import auth

from ninja_extra import NinjaExtraAPI, api_controller, route, status
from ninja_extra.permissions import AllowAny
from ninja import File, Form, UploadedFile

from utils import DEFAULT_CACHE_DURATION, JSON_CONTENT_TYPE, serializer_encoder
from asgiref.sync import sync_to_async
import asyncio

api = NinjaExtraAPI(
    title="Bdaya Team Api",
    version="1.1.0",
    renderer=RawJsonMSGRenderer(),
    auth=AsyncCookiesJWTAuth(),
    app_name="Bdaya Team"
)

def create_member_transaction(payload: api_schemas.RegisterRequest) -> Member:
    try:
        with transaction.atomic():
            track = get_object_or_404(Track, id=payload.request_track_id)
            
            counter, _ = TrackCounter.objects.select_for_update().get_or_create(
                track=track
            )
            counter.current_value += 1
            counter.save()
            
            code = f"{track.prefix}-{counter.current_value}"
            GENERATED_PASSWORD = f"{code}@{payload.collage_code}"

            user = BdayaUser(
                email=payload.email,
                username=payload.name,
                phone_number=payload.phone_number,
                track=track,
                role=UserRole.MEMBER,
            )
            user.set_password(GENERATED_PASSWORD)
            user.save()

            member = Member.objects.create(
                bdaya_user=user,
                code=code,
                collage_code=payload.collage_code,
                track=track
            )

            transaction.on_commit(
                lambda: send_member_email(
                    user.username,
                    user.email,
                    GENERATED_PASSWORD,
                    member.code,
                    track.name,
                )
            )

            return member
            
    except IntegrityError:
        raise ValueError("something went wrong, Please try again.")

@api_controller('', tags=['Auth'], permissions=[AllowAny])
class AuthController:

    @route.post("/login/", throttle=AsyncSafeThrottle("10/1h"), auth=None, response={200: api_schemas.LoginResponse, 400: api_schemas.ErrorResponse, 429: api_schemas.SingleErrorResponse})
    async def login(self, request: HttpRequest, payload: api_schemas.LoginRequest):
        
        user: BdayaUser | None = await auth.aauthenticate(request, email=payload.email, password=payload.password) # type: ignore

        if not user:
            return 400, {"details": "invalid email or password"}

        user = await BdayaUser.objects.select_related('track', 'member').aget(id=user.id) # type: ignore
        
        track_data = None
        if not user.is_organizer and user.track:
            track_data = TrackNameOnlyMSGSerializer.from_model(user.track)

        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        if user.is_member and hasattr(user, "member"):
            refresh['code'] = user.member.code # type: ignore
            
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        encoded_data = serializer_encoder.encode({
            "username": user.username,
            "is_admin": user.is_superuser,
            "role": user.role,
            "track": track_data,
        })
        
        csrf.get_token(request)
        response = HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE) 
        response.set_cookie(
            key="access_token",
            value=access_token,
            expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            secure=True,
            httponly=True,
            samesite='Lax'
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=True,
            httponly=True,
            samesite='Lax'
        )
        
        return response

    @route.get("/logout/", response={204: None, 401: api_schemas.ErrorResponse})
    async def logout(self, request: HttpRequest, response: HttpResponse):
        auth.logout(request)
        response.delete_cookie("csrftoken")
        response.delete_cookie("sessionid")
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return status.HTTP_204_NO_CONTENT, {}
  
    @route.post("/register/", throttle=AsyncSafeThrottle("10/1h"), auth=None, response={201: api_schemas.RegisterResponse, 400: dict[str, str], 422: api_schemas.PydanticErrorResponse, 429: api_schemas.SingleErrorResponse})
    async def register(self, payload: api_schemas.RegisterRequest):
        errors: dict[str, str] = {}
        email_exists, phone_exists, collage_code_exists = await asyncio.gather(
            BdayaUser.objects.filter(email=payload.email).aexists(),
            BdayaUser.objects.filter(phone_number=payload.phone_number).aexists(),
            Member.objects.filter(collage_code=payload.collage_code).aexists()
        )
        
        if email_exists:
            errors["email"] = str(_("email_exists"))
        
        if phone_exists:
            errors["phone"] = str(_("phone_exists"))
        
        if collage_code_exists:
            errors["collage_code"] = str(_("collage_code_exists"))
            
        if errors:
            return 400, errors

        try:
            member = await sync_to_async(create_member_transaction)(payload)
        except ValueError as e:
            return 400, {"details": str(e)}

        user = await BdayaUser.objects.aget(id=member.bdaya_user_id) # type: ignore

        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        refresh['code'] = member.code
                
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        cache.delete_pattern("*member*") # type: ignore
        
        encoded_data = serializer_encoder.encode({
            "code": member.code,
            "name": user.username,
            "email": user.email,
            "track": TrackNameOnlyMSGSerializer.from_model(member.bdaya_user.track) # type: ignore
        })
        response = HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE, status=status.HTTP_201_CREATED)

        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Lax',
            expires=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='Lax',
            expires=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME')
        )

        return response
        
    @route.post("/token/refresh/", auth=None, response={204: None, 401: api_schemas.ErrorResponse})
    async def refresh_tokens(self, request: HttpRequest, payload: api_schemas.RefreshTokenRequest, response: HttpResponse):
        
        raw_refresh = request.COOKIES.get("refresh_token") or payload.refresh
        
        if not raw_refresh:
            return 401, {"details": "Refresh token missing"}

        try:
            refresh = RefreshToken(raw_refresh) # type: ignore
        except TokenError:
            return 401, {"details": "Refresh token is invalid or expired"}

        access_token = str(refresh.access_token)
        
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    await sync_to_async(refresh.blacklist)()
                except AttributeError:
                    pass
            
            # Mint the new refresh token parameters
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            
        new_refresh_token = str(refresh)

        response.set_cookie(
            key="access_token",
            value=access_token,
            expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
            secure=True,
            httponly=True,
            samesite='Lax'
        )
        
        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            secure=True,
            httponly=True,
            samesite='Lax'
        )

        return status.HTTP_204_NO_CONTENT, {}

    @route.get("/test-auth/", response={200: api_schemas.TestAuthResponse})
    async def test_auth(self, request: HttpRequest):
        track: TrackNameOnlyMSGSerializer | None = None
        USER: BdayaUser = request.user # type: ignore
        
        if not USER.is_organizer:
            track = TrackNameOnlyMSGSerializer.from_model(USER.track) # type: ignore
        
        settings = await sync_to_async(SiteSetting.get_solo)()
        
        encoded_data = serializer_encoder.encode({
            "username": USER.username,
            "is_admin": USER.is_superuser,
            "role": USER.role,
            "track": track,
            "settings": SiteSettingsImagesMSGSerializer.from_model(settings),
        })
        csrf.get_token(request)
        
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)

    @route.post("/notifications/subscribe/", response={204: None})
    async def save_subscription(self, request: HttpRequest, payload: api_schemas.SubscriptionRequest):
        await PushSubscription.objects.aupdate_or_create(
            user=request.user,
            endpoint=payload.endpoint,
            defaults={
                "auth": payload.auth,
                "p256dh": payload.p256dh
            }
        )
        return 204, {}

@api_controller("/tracks/", tags=['Track'], permissions=[NinjaIsOrganizer])
class TracksController:
    
    @route.get("", response={200: list[api_schemas.TrackSchema]}, auth=None, permissions=[AllowAny])
    async def get_all(self):
        cached = await cache.aget(TRACKS_CACHE_KEY)
        
        if cached:
            return HttpResponse(cached, "application/json")

        query_set = Track.objects.defer("prefix").values(
            "id", "name", "image", "en_description", "ar_description"
        )
        track_list = [track async for track in query_set]
        
        data = TrackMSGSerializer.from_queryset_values(track_list)

        encoded_data = serializer_encoder.encode(data)
        await cache.aset(TRACKS_CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        
        return HttpResponse(encoded_data, content_type="application/json")
    
    @route.post('', response={201: None, 400: api_schemas.DetailError})
    async def create(self, payload: Form[api_schemas.TrackCreateSchema], image: UploadedFile = File(...)): # type: ignore
        
        @sync_to_async
        def save_track():
            try:
                Track.objects.create(
                    name=payload.name,
                    prefix=payload.prefix,
                    en_description=payload.en_description,
                    ar_description=payload.ar_description,
                    image=image,
                )
                return True, {}
            except IntegrityError:
                return False, {"detail": "this track already exists"}
        
        success, error_payload = await save_track()
        
        if not success:
            return status.HTTP_400_BAD_REQUEST, error_payload
        
        cache.delete(TRACKS_CACHE_KEY)
        return status.HTTP_201_CREATED, {}
    
    @route.get('/{track_name}/', response={200: api_schemas.TrackSchema}, auth=None, permissions=[AllowAny])
    async def get_one(self, track_name: str):
        CACHE_KEY = track_cache_key(track_name)
        if (data:= await cache.aget(CACHE_KEY)):
            return HttpResponse(data, content_type="application/json")
        
        track = await aget_object_or_404(Track, name=track_name)
        track_encoded = TrackMSGSerializer.from_model(track).encode()
        await cache.aset(CACHE_KEY, track_encoded, DEFAULT_CACHE_DURATION)
        
        return HttpResponse(track_encoded, content_type="application/json")
        
    @route.delete('/{track_name}/', permissions=[NinjaIsSuperUser], response={204: None, 404: api_schemas.ErrorResponse})
    async def delete(self, track_name: str):
        count,_ = await Track.objects.filter(name=track_name).adelete()
        
        if count == 0:
            return status.HTTP_404_NOT_FOUND, {"details": "Track Not Found"}
        
        await cache.adelete_many([TRACKS_CACHE_KEY, track_cache_key(track_name)])
        return status.HTTP_204_NO_CONTENT, {}

@api_controller("/", tags=['Auth'], permissions=[NinjaIsSuperUser])
class ResetAll:
    
    @sync_to_async
    def delete_tracks(self) -> None:
        with transaction.atomic():
            Track.objects.select_for_update().delete()
    
    @route.delete('/reset-all/', response={204: None, 500: api_schemas.ErrorResponse, 403: api_schemas.ErrorResponse})
    async def reset_all(self):
        "Very Dangores, Deletes all tracks and members and tasks and technicals."
        try:
            await self.delete_tracks()
            cache.clear()
            return status.HTTP_204_NO_CONTENT, {}
        except Exception as e:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {"details": repr(e)}


api.register_controllers(
    # ======= core ========
    AuthController,
    TracksController,
    ResetAll,
    
    # ======= organizers =======
    MembersController,
    AttendanceDaysConrtoller,
    SettingsController,
    
    # ======= members ========
    TasksController,
    ProtectedTaskController,
    MemberProfileController,
    MemberEditTaskController,
    
    # ======= technicals ========
    TechnicalTasksController,
    TechnicalMembersController
)