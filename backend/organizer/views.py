from django.http import Http404
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.parsers import MultiPartParser, FormParser

from core.models import Track
from core.permissions import IsOrganizer
from core.serializers import RegisterSerializer
from .serializers import AttendanceDaysSerializer, SiteSettingsSerializer
from .models import (
    Attendance, 
    AttendanceStatus,
    AttendanceAllowedDay, 
    MemberEditType, 
    SiteSetting
)

from member.models import Member
from member.serializers import MemberSerializer

from django.db import transaction
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample, OpenApiParameter

# Create your views here.

class Members(APIView):
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsOrganizer())
        return perms
    
    @extend_schema(
        responses={
            200: MemberSerializer(many=True)
        }
    )
    def get(self, request: Request, track_name: str) -> Response:
        CACHE_KEY = f"members_{track_name}"
        if (data:=cache.get(CACHE_KEY)):
            return Response(data)
        
        members = (
            Member.objects.
            select_related("track")
            .prefetch_related("attendances__date")
            .filter(track__track=track_name)
            .order_by("joined_at")
        )
        data = MemberSerializer(members, many=True).data
        cache.set(CACHE_KEY, data, 180)
        return Response(data)
    
    
class MemberEdit(APIView):
    serializer_class = None
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsOrganizer())
        return perms
    
    def move_member_to_another_track(self, code: str, current_track: str, move_to_track: str) -> None | Http404:
        member = get_object_or_404(Member.objects.defer('code', 'bonus', 'track', 'joined_at'), code=code, track__track=current_track)
        track = get_object_or_404(Track.objects.only('id'), track=move_to_track)
        
        serializer = RegisterSerializer(data={
            "name": member.name,
            "email": member.email,
            "collage_code": member.collage_code,
            "phone_number": str(member.phone_number),
            "request_track_id": track.pk,
        })
        member.delete()
        if serializer.is_valid():
            serializer.save()
        else:
            raise Http404(serializer.errors)
        

    @extend_schema(
        request=inline_serializer(
            "patchMember",
            {
                "code": serializers.CharField(),
                "field": serializers.CharField(),
                "value": serializers.CharField(),
                "type": serializers.ChoiceField(MemberEditType),
                "excuse": serializers.CharField(),
            }
        ),
        examples=[
            OpenApiExample(
                "Update a Field Example",
                {
                    "code": "c-2",
                    "field": "bonus",
                    "value": 2,
                    "type": MemberEditType.DATA,
                    "excuse": None
                },
                request_only=True,
            ),
            OpenApiExample(
                "Create Attendance Example",
                {
                    "code": "c-2",
                    "field": "2026-2-2",
                    "value": AttendanceStatus.PRESENT,
                    "type": MemberEditType.ATTENDANCE,
                    "excuse": None
                },
                request_only=True,
            ),
            OpenApiExample(
                "Update Attendance Example",
                {
                    "code": "c-2",
                    "field": "2026-2-2",
                    "value": AttendanceStatus.EXCUSED,
                    "type": MemberEditType.ATTENDANCE,
                    "excuse": "tired"
                },
                request_only=True
            ),
            OpenApiExample(
                "Update Member Track Example",
                {
                    "code": "c-2",
                    "field": "track",
                    "value": "Python",
                    "type": MemberEditType.DATA,
                    "excuse": None
                },
                request_only=True
            ),
        ]
    )
    @transaction.atomic
    def post(self, request: Request, track_name: str) -> Response:
        field: str = request.data.get("field") # type: ignore
        value: str | int = request.data.get("value") # type: ignore
        excuse: str | None = request.data.get("excuse") # type: ignore
        code: str = request.data.get("code") # type: ignore
        CACHE_KEY = f"members_{track_name}"
        
        try:
            req_type: MemberEditType = MemberEditType(request.data.get("type")) # type: ignore
        except ValueError:
            return Response({"details": "Bad request type"}, status=status.HTTP_400_BAD_REQUEST)
        
        member: Member = get_object_or_404(Member, code=code)
        match req_type:
            case MemberEditType.ATTENDANCE:
                try:
                    AttendanceStatus(value)
                except ValueError:
                    return Response({"details": "bad status option"}, status=status.HTTP_400_BAD_REQUEST)
                
                if Attendance.objects.filter(member=member, date__day=field).exists():
                    Attendance.objects.filter(member=member, date__day=field).update(status=value, excuse_reason=excuse)
                    cache.delete(CACHE_KEY)
                else:
                    day = get_object_or_404(AttendanceAllowedDay.objects.only('id'), day=field)
                    Attendance.objects.create(member=member, date=day, status=value)
                    cache.delete(CACHE_KEY)
                    return Response(status=status.HTTP_201_CREATED)
            case MemberEditType.DATA:
                if field == "track":
                    self.move_member_to_another_track(code, track_name, str(value))
                    cache.delete(CACHE_KEY)
                    return Response()
                else:
                    settings = SiteSetting.get_solo()
                    if not field in settings.organizer_can_edit:
                        return Response({"details": f"field {field} is not allowed"}, status=status.HTTP_403_FORBIDDEN)
                    
                    Member.objects.filter(code=code).update(**{field: value})
                    cache.delete(CACHE_KEY)
            case _:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response()

class AttendanceDayApi(APIView):
    serializer_class = AttendanceDaysSerializer(many=True)
    
    def get_cache(self, track: str) -> str:
        return f"attendance_days_{track}"
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsOrganizer())
        return perms

    def get(self, request: Request, track_name: str) -> Response:
        CACHE_KEY = self.get_cache(track_name)
        
        if (data:=cache.get(CACHE_KEY)):
            return Response(data)
        
        days = AttendanceAllowedDay.objects.select_related("track").filter(track__track=track_name)
        data = AttendanceDaysSerializer(days, many=True).data
        cache.set(CACHE_KEY, data, 300)
        return Response(data)
    
    @extend_schema(
        request=AttendanceDaysSerializer,
        responses={
            201: AttendanceDaysSerializer,
            400: inline_serializer(
                name="bad_day",
                fields= {
                    "field_name": serializers.CharField()
                }
            )
        }
    )
    def post(self, request: Request, track_name: str) -> Response:
        day = request.data.get("day") # type: ignore
        try:
            if AttendanceAllowedDay.objects.filter(day=day, track__track=track_name).exists(): # type: ignore
                return Response({"details": "this day already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            track = get_object_or_404(Track.objects.only("id"), track=track_name)
            attendance = AttendanceAllowedDay.objects.create(day=day, track=track)
            cache.delete(self.get_cache(track_name))
            return Response(AttendanceDaysSerializer(attendance).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"details": e}, status=status.HTTP_400_BAD_REQUEST)
    
    
    @extend_schema(
        parameters=[OpenApiParameter("day", OpenApiTypes.STR)],
        responses={
            201: AttendanceDaysSerializer,
            400: inline_serializer(
                name="bad_day",
                fields= {
                    "field_name": serializers.CharField()
                }
            )
        }
    )
    def delete(self, request: Request, track_name: str) -> Response:
        day = request.query_params.get("day")
        try:
            if not AttendanceAllowedDay.objects.filter(day=day, track__track=track_name).exists():
                return Response({"details": "No Day Found"}, status=status.HTTP_400_BAD_REQUEST)
            
            AttendanceAllowedDay.objects.filter(day=day, track__track=track_name).delete()
            return Response()
        except:
            return Response({"details": "somthing went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        
    @extend_schema(
        request=inline_serializer(
            "updateDay",
            {
                "oldDay": serializers.CharField(),
                "newDay": serializers.CharField(),
            }
        ),
        responses={
            201: None,
            400: None,
            404: inline_serializer(
                name="day_not_found",
                fields= {
                    "field_name": serializers.CharField()
                }
            )
        }
    )
    def put(self, request: Request, track_name: str) -> Response:
        old_day = request.data.get("oldDay") # type: ignore
        new_day = request.data.get("newDay") # type: ignore
        attendace = get_object_or_404(AttendanceAllowedDay.objects.only("day"), track__track=track_name, day=old_day)
        if attendace.day == new_day:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        attendace.day = new_day # type: ignore
        attendace.save()
        cache.delete(self.get_cache(track_name))
        return Response()


class SettingsApi(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = SiteSettingsSerializer
    
    def get_permissions(self):
        perms = super().get_permissions()
        perms.append(IsOrganizer())
        return perms
    
    def get(self, request: Request) -> Response:
        site = SiteSetting.get_solo()
        serializer = SiteSettingsSerializer(site)
        return Response(serializer.data)
    
    def put(self, request: Request) -> Response:
        obj = SiteSetting.get_solo()
        serializer = SiteSettingsSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

