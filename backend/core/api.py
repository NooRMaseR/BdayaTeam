from member.models import Member
from organizer.models import SiteSetting
from organizer.serializers import SiteSettingsImagesMSGSerializer

from .serializers import TrackMSGSerializer, TrackNameOnlyMSGSerializer
from .permissions import IsOrganizer, IsSuperUser, JWTCookiesAuthentication
from .models import BdayaUser, Track, TrackCounter, UserRole
from .tasks import delete_all_tracks, send_member_email
from .caches import TRACKS_CACHE_KEY, track_cache_key
from .auth import JWT_COOKIES_AUTH
from . import api_schemas

from django.db import IntegrityError, transaction, connection
from django.utils.translation import gettext_lazy as _
from django.db.utils import OperationalError
from django.core.cache import cache, caches
from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.conf import settings
from django.contrib import auth

from utils import DEFAULT_CACHE_DURATION, STORE, JSON_CONTENT_TYPE, generate_jwts_for_user, serializer_encoder
from asgiref.sync import sync_to_async
from typing import Annotated
import asyncio
import jwt

from django_bolt.exceptions import BadRequest, NotFound, InternalServerError
from django_bolt.health import register_health_checks, add_health_check
from django_bolt.param_functions import Form
from django_bolt import (
    IsAuthenticated,
    OpenAPIConfig,
    Response,
    BoltAPI,
    Request,
    status,
    JSON,
)

bolt = BoltAPI(
    prefix="/api/",
    trailing_slash='append',
    openapi_config=OpenAPIConfig(
        title="Bdaya Team Api",
        version="1.2.0",
        path="/api/docs",
        enabled=True
    ),
    validate_response=False,
    django_middleware=settings.BOLT_MIDDLEWARE
)

bolt.mount_django("/")
register_health_checks(bolt)

@sync_to_async(thread_sensitive=True)
def database_check() -> tuple[bool, str]:
    try:
        connection.ensure_connection()
        return True, "ok"
    except OperationalError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

async def redis_check() -> tuple[bool, str]:
    try:
        cache = caches['default'] 
        
        await cache.aset("health_ping", "pong", timeout=1)
        val = await cache.aget("health_ping")
        
        if val == "pong":
            return True, "ok"
        return False, "Cache connected but returned invalid data"
    except Exception as e:
        return False, f"Cache error: {str(e)}"

add_health_check(database_check)
add_health_check(redis_check)


@bolt.post("/login/", tags=['Auth'], response_model=api_schemas.LoginResponseMSG)
async def login(request: Request, body: api_schemas.LoginRequestMSG):
    """Login
    
    a login endpoint with the cookies
    """
    user: BdayaUser | None = await auth.aauthenticate(request, email=body.email, password=body.password) # type: ignore

    if not user:
        raise BadRequest(detail="invalid email or password")

    user = await BdayaUser.objects.select_related('track', 'member').aget(id=user.id) # type: ignore
    
    track_data = None
    if not user.is_organizer and user.track:
        track_data = TrackNameOnlyMSGSerializer.from_model(user.track)
    
    tokens = generate_jwts_for_user(user)

    data = api_schemas.LoginResponseMSG(
        username= user.username,
        is_admin= user.is_superuser,
        role= UserRole(user.role),
        track= track_data,
    )
    
    response = JSON(data) \
    .set_cookie(
        name="access_token",
        value=tokens.access,
        max_age=tokens.access_exp,
        secure=True,
        httponly=True,
    ) \
    .set_cookie(
        name='refresh_token',
        value=tokens.refresh,
        max_age=tokens.refresh_exp,
        secure=True,
        httponly=True,
    )
    
    return response

@bolt.get("/logout/", status_code=204, tags=["Auth"])
async def logout(request: Request):
    """Logout
    A Logout endpoint that removes the cookies from the user `cookies`
    
    this endpoint is also stores the token in the `revokation store`
    """
    
    token = request.cookies.get('access_token')
    if not token:
        token = request.headers.get("authorization")
        if token:
            token = token.split(' ')[1]
    
    if token:
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            
            jti = payload.get("jti")
            exp = payload.get("exp")
            
            if jti and exp:
                await STORE.revoke(jti=jti, exp=exp)
                
        except jwt.DecodeError:
            pass
    
    response = Response(status_code=204) \
    .delete_cookie("csrftoken") \
    .delete_cookie("sessionid") \
    .delete_cookie("access_token") \
    .delete_cookie("refresh_token")
    return response

@bolt.post("/register/", status_code=201, tags=['Auth'], response_model=api_schemas.RegisterResponseMSG)
async def register(payload: api_schemas.RegisterRequestMSG):
    "Register"
    
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
        return JSON(errors, status.HTTP_400_BAD_REQUEST)

    try:
        member = await sync_to_async(create_member_transaction)(payload)
    except ValueError as e:
        raise BadRequest(detail=str(e))

    user = await BdayaUser.objects.select_related("member").aget(id=member.bdaya_user_id) # type: ignore

    tokens = generate_jwts_for_user(user)
    
    cache.delete_pattern("*member*") # type: ignore
    
    data = api_schemas.RegisterResponseMSG(
        code = member.code,
        name = user.username,
        email = user.email,
        track = TrackNameOnlyMSGSerializer.from_model(member.bdaya_user.track) # type: ignore
    )
    response = JSON(data, status_code=status.HTTP_201_CREATED) \
    .set_cookie(
        name='access_token',
        value=tokens.access,
        httponly=True,
        secure=True,
        samesite='Lax',
        max_age=tokens.access_exp,
    ).set_cookie(
        name='refresh_token',
        value=tokens.refresh,
        httponly=True,
        secure=True,
        samesite='Lax',
        max_age=tokens.refresh_exp
    )

    return response

@bolt.post("/token/refresh/", tags=['Auth'], auth=[JWTCookiesAuthentication(token_type="refresh", cookie="refresh_token", require_jti=True, revocation_store=STORE)], guards=[IsAuthenticated()], status_code=204)
async def refresh_tokens(request: Request):
    """Refresh Tokens
    
    refreshes the tokens from the cookies
    
    it looks for the the refresh token in the `cookies`, if not found then search for it in the `payload`
    """
    tokens = generate_jwts_for_user(request.user)
    
    response = Response(status_code=status.HTTP_204_NO_CONTENT) \
    .set_cookie(
        name="access_token",
        value=tokens.access,
        max_age=tokens.access_exp,
        secure=True,
        httponly=True,
        samesite='Lax'
    ).set_cookie(
        name='refresh_token',
        value=tokens.refresh,
        max_age=tokens.refresh_exp,
        secure=True,
        httponly=True,
        samesite='Lax'
    )
    
    return response

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

@bolt.get("/test-auth/", tags=['Auth'], auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated()])
async def new_test_auth(request: Request) -> api_schemas.TestAuthResponseMSG: # type: ignore
    """test authentication
    
    test if the user is authenticated and return the user `credentials`
    """
    user: BdayaUser = request.user
    
    track: TrackNameOnlyMSGSerializer | None = None
    
    if not user.is_organizer:
        track = TrackNameOnlyMSGSerializer.from_model(user.track) # type: ignore
    
    settings = await sync_to_async(SiteSetting.get_solo)()
    
    return api_schemas.TestAuthResponseMSG(
        username= user.username,
        is_admin= user.is_superuser,
        role= UserRole(user.role),
        track= track,
        settings= SiteSettingsImagesMSGSerializer.from_model(settings),
    )


@bolt.get("/tracks/", tags=['Track'], response_model=list[TrackMSGSerializer], validate_response=False)
async def get_all():
    "get all tracks"
    
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

@bolt.post('/tracks/', tags=["Track"], status_code=201, auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsOrganizer])
async def create_track(payload: Annotated[api_schemas.TrackCreateRequestMSG, Form()]): # type: ignore
    """create a track
    
    the `name` and `prefix` must be `unique`
    """
    
    errors: dict[str, str] = {}
    track_exists, prefix_exists = await asyncio.gather(
        Track.objects.filter(name__iexact=payload.name).aexists(),
        Track.objects.filter(prefix__iexact=payload.prefix).aexists(),
    )
    
    if track_exists:
        errors['name'] = str(_("this track already exists"))
    
    if prefix_exists:
        errors['prefix'] = str(_("this prefix already exists"))
        
    if errors:
        return JSON(errors, status.HTTP_400_BAD_REQUEST)
    
    try:
        await Track.objects.acreate(
            name=payload.name,
            prefix=payload.prefix,
            en_description=payload.en_description,
            ar_description=payload.ar_description,
            image=payload.image.file,
        )
    except IntegrityError:
        raise BadRequest(detail=str(_("this track already exists")))
    
    cache.delete(TRACKS_CACHE_KEY)
    return Response(status_code=status.HTTP_201_CREATED)

@bolt.get('/tracks/{track_name}/', tags=['Track'], status_code=200, response_model=TrackMSGSerializer)
async def get_one_track(track_name: str):
    "get one track"
    
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

@bolt.delete('/tracks/{track_name}/', tags=['Track'], status_code=204, auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsSuperUser])
async def delete(track_name: str): # type: ignore
    """delete a track (Very Dangerios)

    this endpoint deletes a track along with `all related fields`
    """
    
    count, _ = await Track.objects.filter(name=track_name).adelete()
    
    if count == 0:
        raise NotFound(detail="Track Not Found")
    
    await cache.adelete_many([TRACKS_CACHE_KEY, track_cache_key(track_name)])
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.delete('/reset-all/', status_code=202, tags=['Auth'], auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsSuperUser])
async def reset_all(): # type: ignore
    """Reset All
    
    `Very Dangerios`, Deletes all tracks and members and tasks and technicals, every thing related to the `tracks`
    """
    
    try:
        delete_all_tracks()
        cache.clear()
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        raise InternalServerError(detail=repr(e))
