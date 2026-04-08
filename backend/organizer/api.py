from ninja import Form, UploadedFile, File
from ninja_extra.permissions import AllowAny
from ninja_extra import route, api_controller, status

from core.permissions import NinjaIsOrganizer, NinjaIsTechnicalOrOrganizer
from core.api_schemas import DetailError, RegisterRequest, ErrorResponse
from core.serializers import TrackNameOnlyMSGSerializer
from core.models import BdayaUser, Track

from member.serializers import MemberORGMSGSerializer
from member.api_schemas import MemebrResponse
from member.models import Member

from .api_schemas import AttendanceDayResponse, DayRequest, DayUpdateRequest, MemberEditGridRequest, SettingsRequest, SettingsResponse
from .caches import SETTINGS_CACHE_KEY, attendance_cache_key, members_by_organizer_cache_key
from .models import Attendance, AttendanceAllowedDay, MemberEditType, SiteSetting
from .serializers import AttendanceDayMSGSerializer, SiteSettingsMSGSerializer

from django.shortcuts import aget_object_or_404, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.db.models import Prefetch
from django.core.cache import cache
from django.db import transaction

from utils import DEFAULT_CACHE_DURATION, JSON_CONTENT_TYPE, serializer_encoder
from asgiref.sync import sync_to_async
from datetime import date

@api_controller("/organizer", tags=['Organizer'], permissions=[NinjaIsOrganizer])
class MembersController:
    
    @route.get("/members/{track_name}/", permissions=[NinjaIsTechnicalOrOrganizer], response={200: list[MemebrResponse]})
    async def get_track_members(self, request: HttpRequest, track_name: str):
        TRACK = track_name.replace("%20", " ")
        USER: BdayaUser = request.user # type: ignore
        track: Track = USER.track # type: ignore

        if USER.is_technical and track.name != TRACK:
            return status.HTTP_403_FORBIDDEN, {"details": f"Not Your Track {USER.username}"},
        
        CACHE_KEY = members_by_organizer_cache_key(track_name)
        if cached_data := await cache.aget(CACHE_KEY):
            return HttpResponse(cached_data, content_type=JSON_CONTENT_TYPE)

        target_track = await aget_object_or_404(
            Track.objects.only("id", "name"), name=TRACK
        )
        track_serialized = TrackNameOnlyMSGSerializer.from_model(target_track)

        members = (
            Member.objects
            .prefetch_related(
                Prefetch(
                    "attendances",
                    Attendance.objects.select_related("date", 'by'),
                )
            )
            .select_related("bdaya_user")
            .defer("joined_at")
            .filter(track=target_track)
            .order_by("joined_at")
        )
        data = await MemberORGMSGSerializer.afrom_queryset_with_track(members, track_serialized)
        data = serializer_encoder.encode(data)
        
        await cache.aset(CACHE_KEY, data, DEFAULT_CACHE_DURATION)
        return HttpResponse(data, content_type=JSON_CONTENT_TYPE)

    @staticmethod
    def move_member_to_another_track(code: str, current_track: str, move_to_track: str) -> None:
        from core.api import create_member_transaction
        
        member = get_object_or_404(
            Member.objects.select_related("bdaya_user").only("collage_code", "bdaya_user__username", "bdaya_user__email", "bdaya_user__phone_number"),
            code=code,
            track__name=current_track,
        )
        track = get_object_or_404(Track.objects.only("id"), name=move_to_track)

        member.delete()
        create_member_transaction(
            RegisterRequest(
                name = member.bdaya_user.username,
                email = member.bdaya_user.email,
                collage_code = member.collage_code,
                phone_number = str(member.bdaya_user.phone_number),
                request_track_id = track.pk,
            )
        )
        
    @route.post("/members/{track_name}/", response={200: None, 403: ErrorResponse})
    async def edit_member_grid(self, request: HttpRequest, track_name: str, payload: MemberEditGridRequest):
        TRACK = track_name.replace("%20", " ")
        CACHE_KEY = members_by_organizer_cache_key(track_name)

        member: Member = await aget_object_or_404(Member.objects.only('code'), code=payload.code)
        
        @sync_to_async
        def safe_transaction() -> tuple[int, dict]:
            with transaction.atomic():
                match payload.type:
                    case MemberEditType.ATTENDANCE:

                        if Attendance.objects.filter(member=member, date__day=payload.field).exists():
                            Attendance.objects.filter(member=member, date__day=payload.field).update(
                                status=payload.value,
                                excuse_reason=payload.excuse,
                                by=request.user
                            )
                            cache.delete(CACHE_KEY)
                        else:
                            day = get_object_or_404(
                                AttendanceAllowedDay.objects.only("id"), day=payload.field
                            )
                            Attendance.objects.create(member=member, date=day, status=payload.value, by=request.user)
                            cache.delete(CACHE_KEY)
                            return status.HTTP_200_OK, {}
                    case MemberEditType.DATA:
                        if payload.field == "track":
                            self.move_member_to_another_track(payload.code, TRACK, str(payload.value))
                            cache.delete_many([CACHE_KEY, members_by_organizer_cache_key(str(payload.value))])
                            return status.HTTP_200_OK, {}
                        else:
                            settings = SiteSetting.get_solo()
                            if not payload.field in settings.organizer_can_edit:
                                return status.HTTP_403_FORBIDDEN, {"details": f"field {payload.field} is not allowed"}

                            Member.objects.filter(code=payload.code).update(**{payload.field: payload.value})
                            cache.delete(CACHE_KEY)
                    case _:
                        return status.HTTP_400_BAD_REQUEST, {}
                    
                return status.HTTP_200_OK, {}
                    
        return await safe_transaction()
    

@api_controller("/organizer/attendance", permissions=[NinjaIsOrganizer], tags=["Organizer"])
class AttendanceDaysConrtoller:
    
    @route.get('/{track_name}/days/', permissions=[NinjaIsTechnicalOrOrganizer], response={200: list[AttendanceDayResponse]})
    async def get_attendance_days(self, track_name: str) -> HttpResponse:
        TRACK = track_name.replace("%20", " ")
        CACHE_KEY = attendance_cache_key(TRACK)

        if data := await cache.aget(CACHE_KEY):
            return HttpResponse(data, content_type=JSON_CONTENT_TYPE)

        days = AttendanceAllowedDay.objects.filter(track__name=TRACK).values("id", "day")

        encoded_data = serializer_encoder.encode(
            await AttendanceDayMSGSerializer.afrom_queryset_values(days)
        )
        await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)
    
    @route.post('/{track_name}/days/', response={201: AttendanceDayResponse, 400: ErrorResponse, 404: DetailError})
    async def create_day(self, track_name: str, payload: DayRequest):
        TRACK = track_name.replace("%20", " ")

        try:
            if await AttendanceAllowedDay.objects.filter(day=payload.day, track__name=TRACK).aexists():
                return status.HTTP_400_BAD_REQUEST, {"details": "this day already exists."}

            track = await aget_object_or_404(Track.objects.only("id"), name=TRACK)
            attendance = await AttendanceAllowedDay.objects.acreate(day=payload.day, track=track)
            encoded_data = serializer_encoder.encode(
                AttendanceDayMSGSerializer(id=attendance.pk, day=attendance.day)
            )
            
            cache.delete(attendance_cache_key(TRACK))
            return HttpResponse(
                encoded_data,
                status=status.HTTP_201_CREATED,
                content_type=JSON_CONTENT_TYPE
            )
        except ValidationError as e:
            return HttpResponse(e.messages, status=status.HTTP_400_BAD_REQUEST, content_type=JSON_CONTENT_TYPE)
        
    @route.delete('/{track_name}/days/', response={204: None})
    async def delete_day(self, track_name: str, day: date):
        TRACK = track_name.replace("%20", " ")
        
        await get_object_or_404(AttendanceAllowedDay, day=day, track__name=TRACK).adelete()
        cache.delete(attendance_cache_key(TRACK))
        return status.HTTP_204_NO_CONTENT, {}
    
    @route.put('/{track_name}/days/', response={204: None, 400: ErrorResponse})
    async def update_day(self, track_name: str, payload: DayUpdateRequest):
        TRACK = track_name.replace("%20", " ")

        attendace = await aget_object_or_404(
            AttendanceAllowedDay.objects.only("day"),
            track__name=TRACK,
            day=payload.oldDay,
        )
        if attendace.day == payload.newDay:
            return status.HTTP_400_BAD_REQUEST, {"details": "new day cannot be the same as old day"}

        attendace.day = payload.newDay
        await attendace.asave()
        cache.delete(attendance_cache_key(TRACK))
        return status.HTTP_204_NO_CONTENT, {}


@api_controller("/organizer/settings/", tags=['Organizer'], permissions=[NinjaIsOrganizer])
class SettingsController:
    
    @route.get('', permissions=[AllowAny], response={200: SettingsResponse})
    async def get_settings(self):
        if cached := await cache.aget(SETTINGS_CACHE_KEY):
            return HttpResponse(cached, content_type=JSON_CONTENT_TYPE)

        site = await sync_to_async(SiteSetting.get_solo)()
        encoded_data = SiteSettingsMSGSerializer.from_model(site).encode()
        await cache.aset(SETTINGS_CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
        return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)

    @route.put('', response={204: None})
    async def update_settings(self, request: HttpRequest, payload: Form[SettingsRequest], site_image: File[UploadedFile] | None = File(None), hero_image: File[UploadedFile] | None = File(None)): # type: ignore
        
        @sync_to_async
        def safe_update_settings() -> None:
            obj = SiteSetting.get_solo()
        
            if request.user.is_superuser and payload.is_register_enabled != None:
                obj.is_register_enabled = payload.is_register_enabled
            
            if payload.organizer_can_edit != None:
                obj.organizer_can_edit = payload.organizer_can_edit # type: ignore
            
            if site_image:
                obj.site_image = site_image # type: ignore
            
            if hero_image:
                obj.hero_image = hero_image # type: ignore
            
            obj.save()
        
        await safe_update_settings()
        cache.delete(SETTINGS_CACHE_KEY)

        return status.HTTP_204_NO_CONTENT, {}
