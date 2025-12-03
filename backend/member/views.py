from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, inline_serializer

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from core.permissions import IsMember

from technical.serializers import TaskSerializer
from technical.models import Task
from . import serializers


# Create your views here.
class Tasks(APIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = TaskSerializer
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsMember())
        return perms
    
    def get(self, request: Request, track_name: str) -> Response:
        tasks = Task.objects.select_related("track").filter(track__track__iexact=track_name)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=inline_serializer(
            "task-member-input",
            {
                "task_id": serializers.serializers.IntegerField(),
                "file": serializers.serializers.FileField(),
                "notes": serializers.serializers.CharField()
            }
        ),
        responses={
            201: None
        }
    )
    @transaction.atomic
    def post(self, request: Request, track_name: str) -> Response:
        print(track_name)
        print(request.data)
        print(request.FILES)
        
        return Response(status=status.HTTP_201_CREATED)
        
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        