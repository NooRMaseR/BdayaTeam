from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListCreateAPIView

from django.contrib import auth
from django.db import transaction
from django.middleware import csrf
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema, inline_serializer

from member.models import Member
from . import models, serializers

# Create your views here.

TOKEN_COOKIE_SETTINGS = {
    "key": "auth_token",
    "samesite": 'Lax',
    "httponly": True,
    "secure": False, #! True in production
    "max_age": 60*60*24*7, # 7 days
}

class Login(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    @extend_schema(
        tags=(
            "Auth",
        ),
        request=inline_serializer(
            "login",
            {
                "email": serializers.serializers.EmailField(),
                "password": serializers.serializers.CharField(),
            },
        ),
        responses={
            200: serializers.LoginSerializer,
            404: inline_serializer(
                "email-is-incorrect",
                {
                    "details": serializers.serializers.CharField(
                        default="No BdayaUser matches the given query"
                    )
                },
            ),
            400: inline_serializer(
                "password-is-incorrect",
                {
                    "details": serializers.serializers.CharField(
                        default="invalid email or password"
                    )
                },
            ),
        },
    )
    def post(self, request: Request) -> Response:
        user: models.BdayaUser | None = auth.authenticate(request._request, email=request.data.get("email"), password=request.data.get("password")) # type: ignore
        track = None
        
        if not user:
            return Response(
                {"details": "invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_obj, _ = Token.objects.get_or_create(user=user)
        
        if user.is_technical:
            track = serializers.TrackSerializer(user.track).data
        elif user.is_member:
            try:
                member = Member.objects.only("code", "track").select_related("track").get(email=user.email)
                track = serializers.TrackSerializer(member.track).data # type: ignore
            except Member.DoesNotExist:
                pass
        
        response = Response(
            {
                "username": user.username,
                "role": user.role,
                "track": track
            }
        )
        response.set_cookie(
            value=token_obj.key,
            **TOKEN_COOKIE_SETTINGS
        )
        
        csrf.get_token(request._request)
        return response
    
class TestAuthCredentials(APIView):
    serializer_class = inline_serializer(
        name="test_auth",
        fields={
            "username": serializers.serializers.CharField(),
            "role": serializers.serializers.ChoiceField(models.UserRole),
            "track": serializers.TrackSerializer()
        }
    )
    

    @extend_schema(
        tags=("Auth",)
    )
    def get(self, request: Request) -> Response:
        track = None
        
        if request.user.is_technical:
            track = serializers.TrackSerializer(request.user.track).data
        elif request.user.is_member:
            try:
                member = Member.objects.only("code", "track").select_related("track").get(email=request.user.email)
                track = serializers.TrackSerializer(member.track).data # type: ignore
            except Member.DoesNotExist:
                pass
        
        return Response(
            {
                "username": request.user.username,
                "role": request.user.role,
                "track": track
            }
        )

@extend_schema(
    tags=("Auth",)
)
class Logout(APIView):
    serializer_class = None
    
    def get(self, request: Request) -> Response:
        response = Response()
        response.delete_cookie(TOKEN_COOKIE_SETTINGS["key"])
        return response


@extend_schema(
    tags=(
        "Auth",
    ),
    request=serializers.RegisterSerializer,
    responses={
        200: serializers.RegisterSerializer,
        400: inline_serializer(
            "bad-register",
            {
                "email": serializers.serializers.ListField(default=["an error for email"])
            }
        )
    }
)
class Register(APIView):
    permission_classes = (AllowAny,)
    
    @transaction.atomic
    def post(self, request: Request) -> Response:
        data = serializers.RegisterSerializer(data=request.data)
        
        if data.is_valid():
            data.save()
            user = get_object_or_404(models.BdayaUser, email=data.validated_data.get("email")) # type: ignore
            token_obj, _ = Token.objects.get_or_create(user=user)
            response = Response(data.data, status=status.HTTP_201_CREATED)
            response.set_cookie(
                value=token_obj.key,
                **TOKEN_COOKIE_SETTINGS
            )
            return response
        else:
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)
        

class Tracks(ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.TrackSerializer
    queryset = models.Track.objects.defer("prefix")
    
    @method_decorator(cache_page(60 * 3)) # 3 minutes
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
