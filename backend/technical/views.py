from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, inline_serializer

from core.permissions import require_technical
from . import models, serializers

# Create your views here.


@extend_schema(
    responses={
        200: serializers.TaskSerializer,
        403: inline_serializer(
            name="Forbidden",
            fields={
                "details": serializers.serializers.CharField(default="Only technicals Allowed")
            }
        )
    }
)
class Tasks(APIView):
    
    @method_decorator(require_technical)
    def get(self, request: Request) -> Response:
        data = models.Task.objects.filter(track=request.user.technical_profile.track)
        return Response(serializers.TaskSerializer(data, many=True).data)