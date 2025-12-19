from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, serializers

from core.permissions import IsOrganizer
from .models import Attendance, AttendanceStatus

from member.models import Member
from member.serializers import MemberSerializer

from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer

# Create your views here.

class Members(APIView):
    serializer_class = MemberSerializer(many=True)
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsOrganizer())
        return perms
    
    def get(self, request: Request, track_name: str) -> Response:
        members = Member.objects.select_related("track").prefetch_related("attendances").filter(track__track__iexact=track_name)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        request=inline_serializer(
            "attendencePost",
            {
                "member_code": serializers.CharField(),
                "status": serializers.ChoiceField(AttendanceStatus),
                "excuse": serializers.CharField(required=True)
            }
        ),
        responses={
            201: None,
            404: inline_serializer(
                "MemberNotFound",
                {
                    "details": serializers.CharField(default="No Member matches the given query.")
                }
            ),
            406: inline_serializer(
                "attendenceNotAcceptable",
                {
                    "details": serializers.CharField(default="this member already has attendence")
                }
            )
        }
    )
    def post(self, request: Request, track_name: str) -> Response:
        if Attendance.objects.only("id").filter(member_id=request.data.get("member_code"), date=timezone.now().date()).exists(): # type: ignore
            return Response({"details": "this member already has attendence"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        try:
            new_status = AttendanceStatus(request.data.get("status")) # type: ignore
        except ValueError:
            return Response({"details": "bad status option"}, status=status.HTTP_400_BAD_REQUEST)
        
        Attendance.objects.create(
            member_id=request.data.get("member_code"), # type: ignore
            status=new_status,
            excuse_reason=request.data.get("excuse") # type: ignore
        )
        return Response(status=status.HTTP_201_CREATED)
    
    
    @extend_schema(
        request=inline_serializer(
            "attendencePut",
            {
                "member_code": serializers.CharField(),
                "status": serializers.ChoiceField(AttendanceStatus),
                "excuse": serializers.CharField(required=True, allow_null=True)
            }
        ),
        responses={
            201: None,
            404: inline_serializer(
                "AttendanceNotFound",
                {
                    "details": serializers.CharField(default="No Attendance matches the given query.")
                }
            )
        }
    )
    def put(self, request: Request, track_name: str) -> Response:
        attendence = get_object_or_404(Attendance, member_id=request.data.get("member_code"), track__track=track_name, date=timezone.now().date()) # type: ignore
        try:
            new_status = AttendanceStatus(request.data.get("status")) # type: ignore
        except ValueError:
            return Response({"details": "bad status option"}, status=status.HTTP_400_BAD_REQUEST)
        
        if attendence.status != new_status:
            attendence.status = new_status
            if new_status == AttendanceStatus.EXCUSED:
                if not request.data.get("excuse"): # type: ignore
                    return Response({"details": f"an {AttendanceStatus.EXCUSED} member must add an execuse with it"}, status=status.HTTP_400_BAD_REQUEST)
                
                attendence.excuse_reason = request.data.get("excuse") # type: ignore
            else:
                attendence.excuse_reason = None
            
            attendence.save(update_fields=["excuse_reason", "status"])
        
        return Response()
    
            
        
class MemberBonus(APIView):
    serializer_class = None
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsOrganizer())
        return perms
    
    @extend_schema(
        request=inline_serializer(
            "bonus",
            {
                "member_code": serializers.CharField(),
                "bonus": serializers.IntegerField()
            }
        )
    )
    def post(self, request: Request) -> Response:
        Member.objects.filter(code=request.data.get("member_code")).update(bonus=request.data.get("bonus")) # type: ignore
        return Response()
