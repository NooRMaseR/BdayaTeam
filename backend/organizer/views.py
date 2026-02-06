from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiParameter,
)

from core.models import Track
from core.api_schemas import RegisterMemberSerializer
from core.permissions import IsOrganizer, IsTechnicalOrOrganizer

from organizer.serializers import AttendanceDayMSGSerializer, AttendanceMSGSerializer, SiteSettingsMSGSerializer
from member.api_schemas import MemberSerializer
from member.auth import RawJsonRenderer
from member.models import Member
from member.serializers import (
    TrackNameOnlyMSGSerializer,
    MemberMSGSerializer, 
)

from django.http import Http404
from django.db import transaction
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


from .api_schemas import AttendanceDaysSerializer, SiteSettingsSerializer
from utils import DEFAULT_CACHE_DURATION, serializer_encoder
from .models import (
    Attendance,
    AttendanceStatus,
    AttendanceAllowedDay,
    MemberEditType,
    SiteSetting,
)

# Create your views here.

class Members(APIView):
    permission_classes = (IsTechnicalOrOrganizer,)
    renderer_classes = (RawJsonRenderer,)

    @extend_schema(responses={200: MemberSerializer(many=True)})
    def get(self, request: Request, track_name: str) -> Response:
        TRACK = track_name.replace("%20", " ")
        
        if request.user.is_technical and request.user.track.track != TRACK:
            return Response({"details": f"Not Your Track {request.user.username}"}, status=status.HTTP_403_FORBIDDEN)

        CACHE_KEY = f"members_{TRACK}"
        if cached_data := cache.get(CACHE_KEY):
            return Response(cached_data)
        
        target_track = get_object_or_404(Track.objects.only("id", "track"), track=TRACK)
        track_object = TrackNameOnlyMSGSerializer(id=target_track.pk, track=target_track.track)

        members = (
            Member.objects.select_related("track")
            .prefetch_related("attendances", 'attendances__date')
            .filter(track=target_track)
            .order_by("joined_at")
            .iterator(300)
        )
        
        data = [
            MemberMSGSerializer(
                code=m.code,
                name=m.name,
                email=m.email,
                collage_code=m.collage_code,
                phone_number=m.phone_number,
                joined_at=m.joined_at,
                status=m.status,
                bonus=m.bonus,
                track=track_object,
                attendances=[
                    AttendanceMSGSerializer(
                        date=AttendanceDayMSGSerializer(
                            id=a.date.id,
                            day=a.date.day,
                        ),
                        status=a.status,
                        excuse_reason=a.excuse_reason
                    ) 
                    for a in m.attendances.all() # type: ignore
                ]
            )
            for m in members
        ]
        
        data = serializer_encoder.encode(data)
        cache.set(CACHE_KEY, data, DEFAULT_CACHE_DURATION)
        return Response(data)
    
    
class MemberEdit(APIView):
    serializer_class = None
    permission_classes = (IsOrganizer,)

    def move_member_to_another_track(self, code: str, current_track: str, move_to_track: str) -> None:
        member = get_object_or_404(
            Member.objects.defer("code", "bonus", "track", "joined_at"),
            code=code,
            track__track=current_track,
        )
        track = get_object_or_404(Track.objects.only("id"), track=move_to_track)

        serializer = RegisterMemberSerializer(
            data={
                "name": member.name,
                "email": member.email,
                "collage_code": member.collage_code,
                "phone_number": str(member.phone_number),
                "request_track_id": track.pk,
            }
        )
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
            },
        ),
        examples=[
            OpenApiExample(
                "Update a Field Example",
                {
                    "code": "c-2",
                    "field": "bonus",
                    "value": 2,
                    "type": MemberEditType.DATA,
                    "excuse": None,
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
                    "excuse": None,
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
                    "excuse": "tired",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Update Member Track Example",
                {
                    "code": "c-2",
                    "field": "track",
                    "value": "Python",
                    "type": MemberEditType.DATA,
                    "excuse": None,
                },
                request_only=True,
            ),
        ],
    )
    @transaction.atomic
    def post(self, request: Request, track_name: str) -> Response:
        field: str = request.data.get("field")  # type: ignore
        value: str | int = request.data.get("value")  # type: ignore
        excuse: str | None = request.data.get("excuse")  # type: ignore
        code: str = request.data.get("code")  # type: ignore
        TRACK = track_name.replace("%20", " ")
        CACHE_KEY = f"members_{TRACK}"

        try:
            req_type: MemberEditType = MemberEditType(request.data.get("type"))  # type: ignore
        except ValueError:
            return Response(
                {"details": "Bad request type"}, status=status.HTTP_400_BAD_REQUEST
            )

        member: Member = get_object_or_404(Member, code=code)
        match req_type:
            case MemberEditType.ATTENDANCE:
                try:
                    AttendanceStatus(value)
                except ValueError:
                    return Response(
                        {"details": "bad status option"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if Attendance.objects.filter(member=member, date__day=field).exists():
                    Attendance.objects.filter(member=member, date__day=field).update(
                        status=value, excuse_reason=excuse
                    )
                    cache.delete(CACHE_KEY)
                else:
                    day = get_object_or_404(
                        AttendanceAllowedDay.objects.only("id"), day=field
                    )
                    Attendance.objects.create(member=member, date=day, status=value)
                    cache.delete(CACHE_KEY)
                    return Response(status=status.HTTP_201_CREATED)
            case MemberEditType.DATA:
                if field == "track":
                    self.move_member_to_another_track(code, TRACK, str(value))
                    cache.delete(CACHE_KEY)
                    return Response()
                else:
                    settings = SiteSetting.get_solo()
                    if not field in settings.organizer_can_edit:
                        return Response(
                            {"details": f"field {field} is not allowed"},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                    Member.objects.filter(code=code).update(**{field: value})
                    cache.delete(CACHE_KEY)
            case _:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response()


class AttendanceDayApi(APIView):
    serializer_class = AttendanceDaysSerializer(many=True)
    permission_classes = (IsTechnicalOrOrganizer,)
    renderer_classes = (RawJsonRenderer,)

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsTechnicalOrOrganizer()]
        return super().get_permissions()

    @staticmethod
    def get_cache_key(track: str) -> str:
        return f"attendance_days_{track}"

    def get(self, request: Request, track_name: str) -> Response:
        TRACK = track_name.replace("%20", " ")
        CACHE_KEY = self.get_cache_key(TRACK)

        if data := cache.get(CACHE_KEY):
            return Response(data)

        days = AttendanceAllowedDay.objects.filter(
            track__track=TRACK
        ).values('id', 'day')
        
        encoded_data = serializer_encoder.encode([
            AttendanceDayMSGSerializer(
                id=day['id'],
                day=day['day'],
            ) 
            for day in days
        ])
        cache.set(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return Response(encoded_data)

    @extend_schema(
        request=AttendanceDaysSerializer,
        responses={
            201: AttendanceDaysSerializer,
            400: inline_serializer(
                name="bad_day", fields={"field_name": serializers.CharField()}
            ),
        },
    )
    def post(self, request: Request, track_name: str) -> Response:
        day = request.data.get("day")  # type: ignore
        TRACK = track_name.replace("%20", " ")
        
        try:
            if AttendanceAllowedDay.objects.filter(day=day, track__track=TRACK).exists():  # type: ignore
                return Response(
                    {"details": "this day already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            track = get_object_or_404(Track.objects.only("id"), track=TRACK)
            attendance = AttendanceAllowedDay.objects.create(day=day, track=track)
            encoded_data = serializer_encoder.encode(
                AttendanceDayMSGSerializer(
                    id=attendance.pk,
                    day=attendance.day
                )
            )
            cache.delete(self.get_cache_key(TRACK))
            return Response(
                encoded_data,
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(e.messages, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[OpenApiParameter("day", OpenApiTypes.STR)],
        responses={
            201: AttendanceDaysSerializer,
            400: inline_serializer(
                name="bad_day", fields={"field_name": serializers.CharField()}
            ),
        },
    )
    def delete(self, request: Request, track_name: str) -> Response:
        day = request.query_params.get("day")
        TRACK = track_name.replace("%20", " ")
        
        query_set = AttendanceAllowedDay.objects.filter(day=day, track__track=TRACK)
        
        try:
            if not query_set.exists():
                return Response(
                    {"details": "No Day Found"}, status=status.HTTP_400_BAD_REQUEST
                )

            query_set.delete()
            cache.delete(self.get_cache_key(TRACK))
            return Response()
        except:
            return Response(
                {"details": "somthing went wrong"}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        request=inline_serializer(
            "updateDay",
            {
                "oldDay": serializers.CharField(),
                "newDay": serializers.CharField(),
            },
        ),
        responses={
            201: None,
            400: None,
            404: inline_serializer(
                name="day_not_found", fields={"field_name": serializers.CharField()}
            ),
        },
    )
    def put(self, request: Request, track_name: str) -> Response:
        old_day = request.data.get("oldDay")  # type: ignore
        new_day = request.data.get("newDay")  # type: ignore
        TRACK = track_name.replace("%20", " ")
        
        attendace = get_object_or_404(
            AttendanceAllowedDay.objects.only("day"),
            track__track=TRACK,
            day=old_day,
        )
        if attendace.day == new_day:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        attendace.day = new_day  # type: ignore
        attendace.save()
        cache.delete(self.get_cache_key(TRACK))
        return Response()


class SettingsApi(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = SiteSettingsSerializer
    permission_classes = (IsOrganizer,)
    CACHE_KEY = "settings"
    
    def get_renderers(self):
        if self.request.method == "GET":
            return [RawJsonRenderer()]
        return super().get_renderers()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request: Request) -> Response:
        if cached := cache.get(self.CACHE_KEY):
            return Response(cached)

        site = SiteSetting.get_solo()
        encoded_data = serializer_encoder.encode(SiteSettingsMSGSerializer(
            site_image=site.site_image.url,
            hero_image=site.hero_image.url,
            is_register_enabled=site.is_register_enabled,
            organizer_can_edit=site.organizer_can_edit
        ))
        cache.set(self.CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return Response(encoded_data)

    def put(self, request: Request) -> Response:
        obj = SiteSetting.get_solo()
        serializer = SiteSettingsSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete(self.CACHE_KEY)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
