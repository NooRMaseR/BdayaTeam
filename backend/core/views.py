from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.parsers import FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema, inline_serializer

from django.contrib import auth
from django.conf import settings
from django.db import transaction
from django.middleware import csrf
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from core.serializers import TrackMSGSerializer, TrackNameOnlyMSGSerializer
from core.permissions import IsOrganizer, IsSuperUser

from member.models import Member
from member.auth import RawJsonRenderer

from organizer.models import SiteSetting
from organizer.api_schemas import SiteSettingsImagesSerializer
from organizer.serializers import SiteSettingsImagesMSGSerializer

from utils import DEFAULT_CACHE_DURATION, serializer_encoder
from . import api_schemas, models
from contextlib import suppress

# Create your views here.

@extend_schema(tags=('Auth',))
class CookiesRefreshTokenView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        access_token = response.data.get("access") # type: ignore
        refresh_token = response.data.get("refresh") # type: ignore
        
        if all([access_token, refresh_token]):
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

class Login(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    renderer_classes = (RawJsonRenderer,)

    @extend_schema(
        tags=("Auth",),
        request=inline_serializer(
            "login",
            {
                "email": api_schemas.serializers.EmailField(),
                "password": api_schemas.serializers.CharField(),
            },
        ),
        responses={
            200: api_schemas.LoginSerializer,
            404: inline_serializer(
                "email-is-incorrect",
                {
                    "details": api_schemas.serializers.CharField(
                        default="No BdayaUser matches the given query"
                    )
                },
            ),
            400: inline_serializer(
                "password-is-incorrect",
                {
                    "details": api_schemas.serializers.CharField(
                        default="invalid email or password"
                    )
                },
            ),
        },
    )
    def post(self, request: Request) -> Response:
        user: models.BdayaUser | None = auth.authenticate(request._request, email=request.data.get("email"), password=request.data.get("password"))  # type: ignore
        track: TrackNameOnlyMSGSerializer | None = None

        if not user:
            return Response(
                {"details": "invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_technical:
            track = TrackNameOnlyMSGSerializer(
                id=user.track.id, # type: ignore
                track=user.track.track # type: ignore
            )
        elif user.is_member:
            with suppress(Member.DoesNotExist):
                member = (
                    Member.objects.only("code", "track_id", "track__track")
                    .select_related("track")
                    .get(email=user.email)
                )
                track = TrackNameOnlyMSGSerializer(id=member.track.id, track=member.track.track)  # type: ignore
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        encoded_data = serializer_encoder.encode({
            "username": user.username, 
            "role": user.role, 
            "track": track,
        })
        
        response = Response(encoded_data)
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
        
        csrf.get_token(request._request)
        return response
        


class TestAuthCredentials(APIView):
    renderer_classes = (RawJsonRenderer,)
    serializer_class = inline_serializer(
        name="test_auth",
        fields={
            "username": api_schemas.serializers.CharField(),
            "role": api_schemas.serializers.ChoiceField(models.UserRole),
            "track": api_schemas.TrackNameOnlySerializer(),
            "settings": SiteSettingsImagesSerializer(),
        },
    )

    @extend_schema(tags=("Auth",))
    def get(self, request: Request) -> Response:
        track: TrackNameOnlyMSGSerializer | None = None

        if request.user.is_technical:
            track = TrackNameOnlyMSGSerializer(
                id=request.user.track.id, 
                track=request.user.track.track
            )
        elif request.user.is_member:
            with suppress(Member.DoesNotExist):
                member = (
                    Member.objects.only("code", "track_id", 'track__track')
                    .select_related("track")
                    .get(email=request.user.email)
                )
                track = TrackNameOnlyMSGSerializer(id=member.track.id, track=member.track.track)  # type: ignore

        settings = SiteSetting.get_solo()
        
        encoded_data = serializer_encoder.encode({
            "username": request.user.username,
            "role": request.user.role,
            "track": track,
            "settings": SiteSettingsImagesMSGSerializer(
                settings.site_image.url,
                settings.hero_image.url
            ),
        })

        return Response(encoded_data)


@extend_schema(tags=("Auth",))
class Logout(APIView):
    serializer_class = None

    def get(self, request: Request) -> Response:
        auth.logout(request._request)
        response = Response()
        response.delete_cookie("csrftoken")
        response.delete_cookie("sessionid")
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


@extend_schema(
    tags=("Auth",),
    request=api_schemas.RegisterMemberSerializer,
    responses={
        200: api_schemas.RegisterMemberSerializer,
        400: inline_serializer(
            "bad-register",
            {
                "email": api_schemas.serializers.ListField(
                    default=["an error for email"]
                )
            },
        ),
    },
)
class Register(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    @transaction.atomic
    def post(self, request: Request) -> Response:
        serializer = api_schemas.RegisterMemberSerializer(data=request.data)

        if serializer.is_valid():
            instance: Member = serializer.save() # type: ignore
            user = get_object_or_404(models.BdayaUser.objects.only('id'), email=instance.email)
            refresh = RefreshToken.for_user(user)
        
            cache.delete_pattern("*member*") # type: ignore
            response = Response(serializer.data, status=status.HTTP_201_CREATED)

            response.set_cookie(
                key='access_token',
                value=str(refresh.access_token),
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Tracks(APIView):
    permission_classes = (IsOrganizer,)
    serializer_class = api_schemas.TrackSerializer(many=True)
    parser_classes = (FormParser, MultiPartParser)
    renderer_classes = (RawJsonRenderer,)
    CACHE_NAME = "tracks"

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request: Request) -> Response:
        cached = cache.get(self.CACHE_NAME)
        if cached:
            return Response(cached)

        query_set = models.Track.objects.defer("prefix").values(
            "id", "track", "image", "description"
        )
        data = [
            TrackMSGSerializer(
                id=track["id"],
                track=track["track"],
                description=track["description"],
                image=track["image"],
            )
            for track in query_set
        ]

        data = serializer_encoder.encode(data)
        cache.set(self.CACHE_NAME, data, DEFAULT_CACHE_DURATION)
        return Response(data)

    @extend_schema(
        request=api_schemas.TrackSerializer,
        responses={
            201: None,
            400: inline_serializer(
                "bad-track",
                {
                    "field": api_schemas.serializers.ListField(
                        default=["an error with this field"]
                    )
                },
            ),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = api_schemas.TrackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(self.CACHE_NAME)
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class DeleteTrack(APIView):
    permission_classes = (IsOrganizer,)

    def delete(self, request: Request, track_name: str) -> Response:
        get_object_or_404(models.Track, track=track_name).delete()
        cache.delete(Tracks.CACHE_NAME)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetAll(APIView):
    permission_classes = (IsSuperUser,)
    serializer_class = None

    @transaction.atomic
    def delete(self, request: Request) -> Response:
        "Very Dangores, Deletes all tracks and members and tasks and technicals."
        try:
            models.Track.objects.select_for_update().delete()
            cache.clear()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"details": repr(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
