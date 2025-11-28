from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer

from . import models, serializers

# Create your views here.

@extend_schema(
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
class Login(APIView):
    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:
        email: str | None = request.data.get("email")  # type: ignore
        password: str | None = request.data.get("password")  # type: ignore

        user = get_object_or_404(models.BdayaUser, email=email)

        if not user.check_password(password): # type: ignore
            return Response(
                {"details": "invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_obj, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "id": user.pk,
                "username": user.username,
                "role": user.role,
                "token": token_obj.key,
            }
        )


class Register(APIView):
    serializer_class = serializers.RegisterSerializer
    
    def post(self, request: Request):
        data = serializers.RegisterSerializer(data=request.data)
        if data.is_valid():
            data.save()
            models.BdayaUser.objects.create(
                username=data.validated_data["username"],
                phone_number=data.validated_data["phone_number"],
                email=data.validated_data["email"]
            )
            return Response(data.data)
        else:
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)