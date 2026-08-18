from core.auth import JWT_COOKIES_AUTH
from core.permissions import (
    IsOrganizer,
    IsTechnicalOrOrganizer,
)
from core.api_schemas import RegisterRequestMSG
from core.models import BdayaUser, Track

from member.serializers import MemberORGMSGSerializer
from member.models import Member, MemberStatus

from .api_schemas import (
    DayRequestMSG,
    DayUpdateRequestMSG,
    MemberEditGridRequestMSG,
    UpdateSettingsRequestMSG,
)
from .caches import (
    SETTINGS_CACHE_KEY,
    attendance_cache_key,
    fired_members_by_organizer_cache_key,
    members_by_organizer_cache_key,
)
from .models import (
    Attendance,
    AttendanceAllowedDay,
    AttendanceStatus,
    MemberEditType,
    SiteSetting,
)
from .serializers import AttendanceDayMSGSerializer, SiteSettingsMSGSerializer

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.core.cache import cache
from django.db import transaction
from django.conf import settings

from utils import DEFAULT_CACHE_DURATION, encode_compress, wrap_compressed_http_response
from asgiref.sync import sync_to_async
from typing import Annotated
from datetime import date

from django_bolt import BoltAPI, IsAuthenticated, Request, Response, status
from django_bolt.exceptions import Forbidden, NotFound, BadRequest
from django_bolt.param_functions import Form

bolt = BoltAPI(
    prefix="/api/organizer/",
    trailing_slash="append",
    validate_response=False,
    django_middleware=settings.BOLT_MIDDLEWARE,
) 


def move_member_to_another_track(code: str, current_track: str, move_to_track: str) -> None:
    from core.api import create_member_transaction

    member = get_object_or_404(
        Member.objects.select_related("bdaya_user").only(
            "collage_code",
            "bdaya_user__username",
            "bdaya_user__email",
            "bdaya_user__phone_number",
        ),
        code=code,
        track__name=current_track,
    )
    track = get_object_or_404(Track.objects.only("id"), name=move_to_track)

    member.delete()
    create_member_transaction(
        RegisterRequestMSG(
            name=member.bdaya_user.username,
            email=member.bdaya_user.email,
            collage_code=member.collage_code,
            phone_number=str(member.bdaya_user.phone_number),
            request_track_id=track.pk,
        )
    )


@bolt.get("/members/{track_name}/", tags=["Organizer"], response_model=list[MemberORGMSGSerializer], auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsTechnicalOrOrganizer])
async def get_unfireed_track_members(request: Request, track_name: str):
    "get track members who's not fired with attendances"
    
    USER: BdayaUser = request.user
    TRACK = track_name.replace("%20", " ")
    track: Track = USER.track  # type: ignore

    if USER.is_technical and track.name != TRACK:
        raise Forbidden(detail=f"Not Your Track {USER.username}")

    CACHE_KEY = members_by_organizer_cache_key(track_name)
    if cached_data := await cache.aget(CACHE_KEY):
        return wrap_compressed_http_response(cached_data)

    try:
        target_track = await Track.objects.only("id", "name").aget(name=TRACK)
    except Track.DoesNotExist:
        raise NotFound(detail=f"Track {track_name} does not exists")
    
    members = (
        Member.objects.prefetch_related(
            Prefetch(
                "attendances",
                Attendance.objects.select_related("date", "by"),
            )
        )
        .select_related("bdaya_user")
        .defer("joined_at")
        .exclude(status=MemberStatus.FIRED)
        .order_by("joined_at")
        .filter(track=target_track)
    )
    data = await MemberORGMSGSerializer.afrom_models(members)
    encoded_data = encode_compress(data)
    await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    return wrap_compressed_http_response(encoded_data)


@bolt.get("/members/{track_name}/fired/", tags=["Organizer"], response_model=list[MemberORGMSGSerializer], auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsTechnicalOrOrganizer])
async def get_fired_track_members(request: Request, track_name: str):
    "get track fired members with attendances"
    
    USER: BdayaUser = request.user
    TRACK = track_name.replace("%20", " ")
    track: Track = USER.track  # type: ignore

    if USER.is_technical and track.name != TRACK:
        raise Forbidden(detail=f"Not Your Track {USER.username}")

    CACHE_KEY = fired_members_by_organizer_cache_key(track_name)
    if cached_data := await cache.aget(CACHE_KEY):
        return wrap_compressed_http_response(cached_data)

    try:
        target_track = await Track.objects.only("id", "name").aget(name=TRACK)
    except Track.DoesNotExist:
        raise NotFound(detail=f"Track {track_name} does not exists")
    

    members = (
        Member.objects.prefetch_related(
            Prefetch(
                "attendances",
                Attendance.objects.select_related("date", "by"),
            )
        )
        .select_related("bdaya_user")
        .defer("joined_at")
        .filter(track=target_track, status=MemberStatus.FIRED)
        .order_by("joined_at")
    )
    data = await MemberORGMSGSerializer.afrom_queryset_values(members)
    encoded_data = encode_compress(data)
    await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    return wrap_compressed_http_response(encoded_data)


@bolt.post("/members/{track_name}/", status_code=204, tags=["Organizer"], auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsOrganizer])
async def edit_member_grid(request: Request, track_name: str, payload: MemberEditGridRequestMSG):
    """edit a member from DataGrid
    
    if the `field=track` then it deletes the user and creates a new user with the new `track`
    """
    
    USER: BdayaUser = request.user
    TRACK = track_name.replace("%20", " ")
    CACHE_KEY = members_by_organizer_cache_key(track_name)

    try:
        member: Member = await Member.objects.only("code").aget(code=payload.code)
    except Member.DoesNotExist:
        raise NotFound(detail=f"Member with code {payload.code} Does not exists")

    @sync_to_async
    def safe_transaction():
        with transaction.atomic():
            match payload.type:
                case MemberEditType.ATTENDANCE:

                    if Attendance.objects.filter(
                        member=member, date__day=payload.field
                    ).exists():
                        Attendance.objects.filter(
                            member=member, date__day=payload.field
                        ).update(
                            status=AttendanceStatus(payload.value),
                            excuse_reason=payload.excuse,
                            by=USER,
                        )
                        cache.delete(CACHE_KEY)
                    else:
                        try:
                            day = AttendanceAllowedDay.objects.only("id").get(
                                day=payload.field
                            )
                        except AttendanceAllowedDay.DoesNotExist:
                            raise NotFound(
                                detail=f"Allowed Day {payload.field} Does not Exists"
                            )

                        Attendance.objects.create(
                            member=member, date=day, status=payload.value, by=USER
                        )
                        cache.delete(CACHE_KEY)
                        return Response(status_code=status.HTTP_204_NO_CONTENT)
                case MemberEditType.DATA:
                    if payload.field == "track":
                        move_member_to_another_track(
                            payload.code, TRACK, str(payload.value)
                        )
                        cache.delete_many(
                            [
                                CACHE_KEY,
                                members_by_organizer_cache_key(str(payload.value)),
                            ]
                        )
                        return Response(status_code=status.HTTP_204_NO_CONTENT)
                    else:
                        settings = SiteSetting.get_solo()
                        if not payload.field in settings.organizer_can_edit:
                            raise Forbidden(
                                detail=f"field {payload.field} is not allowed"
                            )

                        Member.objects.filter(code=payload.code).update(
                            **{payload.field: payload.value}
                        )
                        cache.delete_many(
                            [
                                CACHE_KEY,
                                fired_members_by_organizer_cache_key(TRACK)
                            ]
                        )
                case _:
                    raise BadRequest(detail="unknow type")

            return Response(status_code=status.HTTP_204_NO_CONTENT)

    return await safe_transaction()

@bolt.get("/attendance/{track_name}/days/", response_model=list[AttendanceDayMSGSerializer], auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsTechnicalOrOrganizer])
async def get_attendance_days(track_name: str):
    "get track days for the attendace"
    
    TRACK = track_name.replace("%20", " ")
    CACHE_KEY = attendance_cache_key(TRACK)

    if data := await cache.aget(CACHE_KEY):
        return wrap_compressed_http_response(data)

    days = AttendanceAllowedDay.objects.filter(track__name=TRACK).values("id", "day")

    data = await AttendanceDayMSGSerializer.afrom_queryset_values(days)
    encoded_data = encode_compress(data)
    await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    return wrap_compressed_http_response(encoded_data)

@bolt.post("/attendance/{track_name}/days/", status_code=201, response_model=AttendanceDayMSGSerializer, auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsOrganizer])
async def create_day(track_name: str, payload: DayRequestMSG):
    "create day"
    
    TRACK = track_name.replace("%20", " ")

    try:
        if await AttendanceAllowedDay.objects.filter(
            day=payload.day, track__name=TRACK
        ).aexists():
            raise BadRequest(detail="this day already exists.")

        try:
            track = await Track.objects.only("id").aget(name=TRACK)
        except Track.DoesNotExist:
            raise NotFound(detail=f"Track {TRACK} Does Not Exists")

        attendance = await AttendanceAllowedDay.objects.acreate(
            day=payload.day, track=track
        )
        encoded_data = AttendanceDayMSGSerializer(id=attendance.pk, day=attendance.day).encode()

        cache.delete(attendance_cache_key(TRACK))
        return Response(encoded_data, status_code=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response(
            e.messages,
            status_code=status.HTTP_400_BAD_REQUEST
        )

@bolt.delete("/attendance/{track_name}/days/", status_code=204, auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsOrganizer])
async def delete_day(track_name: str, day: str):
    "delete day"
    
    TRACK = track_name.replace("%20", " ")

    try:
        formated_day = date.fromisoformat(day)
    except:
        raise BadRequest(detail="Invalid date Format")

    await AttendanceAllowedDay.objects.filter(day=formated_day, track__name=TRACK).adelete()
    cache.delete(attendance_cache_key(TRACK))

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.put("/attendance/{track_name}/days/", status_code=204, auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsOrganizer])
async def update_day(track_name: str, payload: DayUpdateRequestMSG):
    "update day"
    
    TRACK = track_name.replace("%20", " ")

    try:
        attendace = await (
            AttendanceAllowedDay.objects.only("day").aget(
                track__name=TRACK,
                day=payload.oldDay,
            )
        )
    except AttendanceAllowedDay.DoesNotExist:
        raise NotFound(detail=f"Day {payload.oldDay} not found")
    
    if attendace.day == payload.newDay:
        raise BadRequest(detail="new day cannot be the same as old day")

    attendace.day = payload.newDay
    await attendace.asave()
    cache.delete(attendance_cache_key(TRACK))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.get("/settings/", response_model=SiteSettingsMSGSerializer)
async def get_settings():
    "get the site settings"
    
    if cached := await cache.aget(SETTINGS_CACHE_KEY):
        return cached

    site = await sync_to_async(SiteSetting.get_solo)()
    data = SiteSettingsMSGSerializer.from_model(site).encode()
    
    await cache.aset(SETTINGS_CACHE_KEY, data, DEFAULT_CACHE_DURATION)
    return data

@bolt.put("/settings/", status_code=204, auth=[JWT_COOKIES_AUTH], guards=[IsAuthenticated(), IsOrganizer])
async def update_settings(request: Request, payload: Annotated[UpdateSettingsRequestMSG, Form()]): # type: ignore
    "update the site settings"

    @sync_to_async
    def safe_update_settings() -> None:
        obj = SiteSetting.get_solo()

        if request.context['auth_claims']['is_superuser'] and payload.is_register_enabled != None:
            obj.is_register_enabled = payload.is_register_enabled

        if payload.organizer_can_edit != None:
            obj.organizer_can_edit = payload.organizer_can_edit  # type: ignore

        if payload.site_image:
            obj.site_image = payload.site_image.file  # type: ignore

        if payload.hero_image:
            obj.hero_image = payload.hero_image.file  # type: ignore

        obj.save()

    await safe_update_settings()
    cache.delete(SETTINGS_CACHE_KEY)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

