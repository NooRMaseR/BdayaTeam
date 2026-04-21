from typing import Annotated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import Member
from organizer.models import SiteSetting
from organizer.serializers import SiteSettingsImagesMSGSerializer

from .serializers import TrackMSGSerializer, TrackNameOnlyMSGSerializer
from .models import BdayaUser, Track, TrackCounter, UserRole
from .permissions import get_any_authenticated_user, get_org_user
from .caches import TRACKS_CACHE_KEY, track_cache_key
from .tasks import delete_all_tracks, send_member_email
from . import api_schemas

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.core.cache import cache
from django.middleware import csrf
from django.conf import settings
from django.contrib import auth

from utils import DEFAULT_CACHE_DURATION, JSON_CONTENT_TYPE, serializer_encoder
from asgiref.sync import sync_to_async
import asyncio

from django_bolt import BoltAPI, Depends, Response, Request, status, OpenAPIConfig
from django_bolt.exceptions import BadRequest, Unauthorized, NotFound, Forbidden
from django_bolt.param_functions import Form, File

bolt = BoltAPI(
    prefix="/api/",
    trailing_slash='append',
    openapi_config=OpenAPIConfig(
        title="Bdaya Team Api",
        version="1.2.0",
        path="/api/docs"
    )
)

def create_member_transaction(payload: api_schemas.RegisterRequestMSG) -> Member:
    try:
        with transaction.atomic():
            try:
                track = Track.objects.get(id=payload.request_track_id)
            except Track.DoesNotExist:
                raise NotFound(detail="Track Does not exists")
            
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

@bolt.post("/login/", tags=['Auth'], response_model=api_schemas.LoginResponseMSG)
async def login(request: Request, body: api_schemas.LoginRequestMSG):
    user: BdayaUser | None = await auth.aauthenticate(request, email=body.email, password=body.password) # type: ignore

    if not user:
        raise BadRequest(detail="invalid email or password")
        # return 400, {"details": "invalid email or password"}

    user = await BdayaUser.objects.select_related('track', 'member').aget(id=user.id) # type: ignore
    
    track_data = None
    if not user.is_organizer and user.track:
        track_data = TrackNameOnlyMSGSerializer.from_model(user.track)
    
    claims = {
        "role": user.role
    }
    if user.is_member and hasattr(user, "member"):
        claims['code'] = user.member.code # type: ignore
    
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    if user.is_member and hasattr(user, "member"):
        refresh['code'] = user.member.code # type: ignore
        
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    encoded_data = {
        "username": user.username,
        "is_admin": user.is_superuser,
        "role": UserRole(user.role),
        "track": track_data,
    }
    
    response = Response(encoded_data) 
    response.set_cookie(
        name="access_token",
        value=access_token,
        expires=str(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds),
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    response.set_cookie(
        name='refresh_token',
        value=refresh_token,
        expires=str(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].seconds),
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    response.set_cookie(
        name='csrftoken',
        value=csrf.get_token(request), # type: ignore
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    
    return response

@bolt.get("/logout/", status_code=204, tags=["Auth"])
async def logout():
    response = Response(status_code=204)
    response.delete_cookie("csrftoken")
    response.delete_cookie("sessionid")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@bolt.post("/register/", status_code=201, tags=['Auth'], response_model=api_schemas.RegisterResponseMSG)
async def register(request: Request, payload: api_schemas.RegisterRequestMSG):
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
        raise BadRequest(detail=errors)

    try:
        member = await sync_to_async(create_member_transaction)(payload)
    except ValueError as e:
        raise BadRequest(detail=str(e))

    user = await BdayaUser.objects.aget(id=member.bdaya_user_id) # type: ignore

    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['code'] = member.code
            
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    cache.delete_pattern("*member*") # type: ignore
    
    encoded_data = {
        "code": member.code,
        "name": user.username,
        "email": user.email,
        "track": TrackNameOnlyMSGSerializer.from_model(member.bdaya_user.track) # type: ignore
    }
    response = Response(encoded_data, status_code=status.HTTP_201_CREATED)
    response.set_cookie(
        name='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        samesite='Lax',
        expires=str(settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').seconds)
    )
    response.set_cookie(
        name='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='Lax',
        expires=str(settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').seconds)
    )
    response.set_cookie(
        name='csrftoken',
        value=csrf.get_token(request), # type: ignore
        secure=True,
        httponly=True,
        samesite='Lax'
    )

    return response

@bolt.post("/token/refresh/", tags=['Auth'], auth=None, status_code=204)
async def refresh_tokens(request: Request, payload: api_schemas.RefreshTokenRequestMSG):
    
    raw_refresh = request.cookies.get("refresh_token") or payload.refresh
    
    if not raw_refresh:
        raise Unauthorized(detail="Refresh token missing")

    try:
        refresh = RefreshToken(raw_refresh) # type: ignore
    except TokenError:
        raise Unauthorized(detail="Refresh token is invalid or expired")

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
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.set_cookie(
        name="access_token",
        value=access_token,
        expires=str(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].seconds),
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    
    response.set_cookie(
        name='refresh_token',
        value=new_refresh_token,
        expires=str(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].seconds),
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    
    response.set_cookie(
        name='csrftoken',
        value=csrf.get_token(request), # type: ignore
        secure=True,
        httponly=True,
        samesite='Lax'
    )

    return response

@bolt.get("/test-auth/", tags=['Auth'], response_model=api_schemas.TestAuthResponseMSG)
async def test_auth(request: Request, user: BdayaUser = Depends(get_any_authenticated_user)): # type: ignore
    track: TrackNameOnlyMSGSerializer | None = None
    
    if not user.is_organizer:
        track = TrackNameOnlyMSGSerializer.from_model(user.track) # type: ignore
    
    settings = await sync_to_async(SiteSetting.get_solo)()
    
    encoded_data = {
        "username": user.username,
        "is_admin": user.is_superuser,
        "role": UserRole(user.role),
        "track": track,
        "settings": SiteSettingsImagesMSGSerializer.from_model(settings),
    }
    
    response = Response(encoded_data)
    response.set_cookie(
        name='csrftoken',
        value=csrf.get_token(request), # type: ignore
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    
    return response

@bolt.get("/tracks/", tags=['Track'], response_model=list[TrackMSGSerializer], validate_response=False)
async def get_all():
    cached = await cache.aget(TRACKS_CACHE_KEY)
    
    if cached:
        return HttpResponse(cached, content_type=JSON_CONTENT_TYPE)

    query_set = Track.objects.defer("prefix").values(
        "id", "name", "image", "en_description", "ar_description"
    )
    track_list = [track async for track in query_set]
    
    data = TrackMSGSerializer.from_queryset_values(track_list)

    encoded_data = serializer_encoder.encode(data)
    await cache.aset(TRACKS_CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    
    return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)

@bolt.post('/tracks/', tags=["Track"], status_code=201)
async def create(name: Annotated[str, Form()], prefix: Annotated[str, Form()], en_description: Annotated[str, Form()], ar_description: Annotated[str, Form()], image: Annotated[list[dict], File(alias="image")] = File(...), user = Depends(get_org_user)): # type: ignore

    errors: dict[str, str] = {}
    track_exists, prefix_exists = await asyncio.gather(
        Track.objects.filter(name__iexact=name).aexists(),
        Track.objects.filter(prefix__iexact=prefix).aexists(),
    )
    
    if track_exists:
        errors['name'] = str(_("this track already exists"))
    
    if prefix_exists:
        errors['prefix'] = str(_("this prefix already exists"))
        
    if errors:
        raise BadRequest(detail=errors)
    try:
        converted_image = SimpleUploadedFile(
            name=image[0]['filename'],
            content=image[0]['content'],
            content_type=image[0]['content_type']
        )
        await Track.objects.acreate(
            name=name,
            prefix=prefix,
            en_description=en_description,
            ar_description=ar_description,
            image=converted_image,
        )
    except IntegrityError:
        raise BadRequest(detail=str(_("this track already exists")))
    
    cache.delete(TRACKS_CACHE_KEY)
    return Response(status_code=status.HTTP_201_CREATED)

@bolt.get('/tracks/{track_name}/', tags=['Track'], status_code=200, response_model=TrackMSGSerializer)
async def get_one(track_name: str):
    CACHE_KEY = track_cache_key(track_name)
    if (data:= await cache.aget(CACHE_KEY)):
        return HttpResponse(data, content_type=JSON_CONTENT_TYPE)
    
    try:
        track = await Track.objects.aget(name=track_name)
    except:
        raise NotFound(detail=f"Track {track_name} Does Not Exists")
    
    track_encoded = TrackMSGSerializer.from_model(track).encode()
    await cache.aset(CACHE_KEY, track_encoded, DEFAULT_CACHE_DURATION)
    
    return HttpResponse(track_encoded, content_type=JSON_CONTENT_TYPE)

@bolt.delete('/tracks/{track_name}/', tags=['Track'], status_code=204)
async def delete(track_name: str, user: BdayaUser = Depends(get_any_authenticated_user)): # type: ignore
    if not user.is_superuser:
        raise Forbidden(detail="Only Admin allowed")
    
    count, _ = await Track.objects.filter(name=track_name).adelete()
    
    if count == 0:
        raise NotFound(detail="Track Not Found")
    
    await cache.adelete_many([TRACKS_CACHE_KEY, track_cache_key(track_name)])
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.delete('/reset-all/', status_code=202, tags=['Auth'])
async def reset_all(user: BdayaUser = Depends(get_any_authenticated_user)): # type: ignore
    "Very Dangores, Deletes all tracks and members and tasks and technicals."
    
    if not user.is_superuser:
        raise Forbidden(detail="Only Admin allowed")
    
    try:
        delete_all_tracks()
        cache.clear()
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        return Response({"details": repr(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
