from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer

from core.serializers import ForbiddenOnlyTechnical
from core.permissions import IsTechnical
from . import models, serializers

# Create your views here.


class Tasks(APIView):
    
    def get_permissions(self):
        perm = super().get_permissions()
        perm.append(IsTechnical())
        return perm
    
    @extend_schema(
        description="Get the Tasks that are related to the technical track",
        responses={
            200: serializers.TaskSerializer(many=True),
            403: ForbiddenOnlyTechnical()
        },
    )
    def get(self, request: Request) -> Response:
        data = models.Task.objects.select_related("track").defer("track__prefix").filter(track=request.user.technical_profile.track)
        return Response(serializers.TaskSerializer(data, many=True).data)
    
    @extend_schema(
        request=serializers.TaskSerializer(),
        responses={
            200: serializers.TaskSerializer(),
            400: inline_serializer(
                "bad-task",
                {
                    "field": serializers.serializers.ListField(default=["field error message"])
                }
            ),
            403: ForbiddenOnlyTechnical()
        }
    )
    def post(self, request: Request) -> Response:
        serializer = serializers.TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        