from typing import Annotated

from core.permissions import (
    get_tech_or_org_user,
    get_org_user,
)
from core.serializers import TrackNameOnlyMSGSerializer
from core.api_schemas import RegisterRequestMSG
from core.models import BdayaUser, Track

from member.serializers import MemberORGMSGSerializer
from member.models import Member

from .api_schemas import (
    AttendanceDayResponseMSG,
    DayRequestMSG,
    DayUpdateRequestMSG,
    MemberEditGridRequestMSG,
)
from .caches import (
    SETTINGS_CACHE_KEY,
    attendance_cache_key,
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

from django.shortcuts import aget_object_or_404, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.http import HttpResponse
from django.core.cache import cache
from django.db import transaction

from utils import DEFAULT_CACHE_DURATION, JSON_CONTENT_TYPE, serializer_encoder
from asgiref.sync import sync_to_async
from datetime import date

from django_bolt import BoltAPI, Depends, Response, UploadFile, status
from django_bolt.exceptions import Forbidden, NotFound, BadRequest
from django_bolt.param_functions import Form, File

bolt = BoltAPI(
    prefix="/api/organizer/",
    trailing_slash="append",
    django_middleware=[
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    validate_response=False,
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


@bolt.get("/members/{track_name}/", tags=["Organizer"], response_model=MemberORGMSGSerializer)
async def get_track_members(track_name: str, user: BdayaUser = Depends(get_tech_or_org_user)):  # type: ignore
    TRACK = track_name.replace("%20", " ")
    track: Track = user.track  # type: ignore

    if user.is_technical and track.name != TRACK:
        raise Forbidden(detail=f"Not Your Track {user.username}")

    CACHE_KEY = members_by_organizer_cache_key(track_name)
    if cached_data := await cache.aget(CACHE_KEY):
        return cached_data

    target_track = await aget_object_or_404(
        Track.objects.only("id", "name"), name=TRACK
    )
    track_serialized = TrackNameOnlyMSGSerializer.from_model(target_track)

    members = (
        Member.objects.prefetch_related(
            Prefetch(
                "attendances",
                Attendance.objects.select_related("date", "by"),
            )
        )
        .select_related("bdaya_user")
        .defer("joined_at")
        .filter(track=target_track)
        .order_by("joined_at")
    )
    data = await MemberORGMSGSerializer.afrom_queryset_with_track(
        members, track_serialized
    )
    data = serializer_encoder.encode(data)

    await cache.aset(CACHE_KEY, data, DEFAULT_CACHE_DURATION)
    return data

@bolt.post("/members/{track_name}/", tags=["Organizer"])
async def edit_member_grid(track_name: str, payload: MemberEditGridRequestMSG, user=Depends(get_org_user)):
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
                            by=user,
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
                            member=member, date=day, status=payload.value, by=user
                        )
                        cache.delete(CACHE_KEY)
                        return Response()
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
                        return Response()
                    else:
                        settings = SiteSetting.get_solo()
                        if not payload.field in settings.organizer_can_edit:
                            raise Forbidden(
                                detail=f"field {payload.field} is not allowed"
                            )

                        Member.objects.filter(code=payload.code).update(
                            **{payload.field: payload.value}
                        )
                        cache.delete(CACHE_KEY)
                case _:
                    raise BadRequest()

            return Response()

    return await safe_transaction()

@bolt.get("/attendance/{track_name}/days/", response_model=list[AttendanceDayResponseMSG])
async def get_attendance_days(track_name: str, user=Depends(get_tech_or_org_user)):
    TRACK = track_name.replace("%20", " ")
    CACHE_KEY = attendance_cache_key(TRACK)

    if data := await cache.aget(CACHE_KEY):
        return HttpResponse(data, content_type=JSON_CONTENT_TYPE)

    days = AttendanceAllowedDay.objects.filter(track__name=TRACK).values("id", "day")

    encoded_data = serializer_encoder.encode(
        await AttendanceDayMSGSerializer.afrom_queryset_values(days)
    )
    await cache.aset(CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    return encoded_data

@bolt.post("/attendance/{track_name}/days/", status_code=201, response_model=AttendanceDayResponseMSG)
async def create_day(track_name: str, payload: DayRequestMSG):
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
        encoded_data = serializer_encoder.encode(
            AttendanceDayMSGSerializer(id=attendance.pk, day=attendance.day)
        )

        cache.delete(attendance_cache_key(TRACK))
        return HttpResponse(
            encoded_data, status=status.HTTP_201_CREATED, content_type=JSON_CONTENT_TYPE
        )
    except ValidationError as e:
        return HttpResponse(
            e.messages,
            status=status.HTTP_400_BAD_REQUEST,
            content_type=JSON_CONTENT_TYPE,
        )

@bolt.delete("/attendance/{track_name}/days/", status_code=204)
async def delete_day(track_name: str, day: str):
    TRACK = track_name.replace("%20", " ")

    try:
        formated_day = date.fromisoformat(day)
    except:
        raise BadRequest(detail="Invalid date Format")

    await AttendanceAllowedDay.objects.filter(day=formated_day, track__name=TRACK).adelete()
    cache.delete(attendance_cache_key(TRACK))

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.put("/{track_name}/days/", status_code=204)
async def update_day(track_name: str, payload: DayUpdateRequestMSG):
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
        return status.HTTP_400_BAD_REQUEST, {
            "details": "new day cannot be the same as old day"
        }

    attendace.day = payload.newDay
    await attendace.asave()
    cache.delete(attendance_cache_key(TRACK))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@bolt.get("/settings/", response_model=SiteSettingsMSGSerializer)
async def get_settings():
    
    if cached := await cache.aget(SETTINGS_CACHE_KEY):
        return HttpResponse(cached, content_type=JSON_CONTENT_TYPE)

    site = await sync_to_async(SiteSetting.get_solo)()
    encoded_data = SiteSettingsMSGSerializer.from_model(site).encode()
    await cache.aset(SETTINGS_CACHE_KEY, encoded_data, DEFAULT_CACHE_DURATION)
    return HttpResponse(encoded_data, content_type=JSON_CONTENT_TYPE)

@bolt.put("/settings/", status_code=204)
async def update_settings(
    is_register_enabled: Annotated[bool, Form()] = False, # type: ignore
    organizer_can_edit: Annotated[list[str], Form()] = [], 
    site_image: Annotated[UploadFile, File(alias="site_image")] = None,  # type: ignore
    hero_image: Annotated[UploadFile, File(alias="hero_image")] = None,  # type: ignore
    user: BdayaUser = Depends(get_org_user)  # type: ignore
):

    @sync_to_async
    def safe_update_settings() -> None:
        obj = SiteSetting.get_solo()

        if user.is_superuser and is_register_enabled != None:
            obj.is_register_enabled = is_register_enabled

        if organizer_can_edit != None:
            
            if isinstance(organizer_can_edit, str):
                cleaned_list = [x.strip() for x in organizer_can_edit.split(",") if x.strip()]
            
            elif isinstance(organizer_can_edit, list) and len(organizer_can_edit) == 1 and "," in organizer_can_edit[0]:
                cleaned_list = [x.strip() for x in organizer_can_edit[0].split(",") if x.strip()]
            else:
                cleaned_list = organizer_can_edit
                
            obj.organizer_can_edit = cleaned_list  # type: ignore

        if site_image:
            obj.site_image = site_image.file  # type: ignore

        if hero_image:
            obj.hero_image = hero_image.file  # type: ignore

        obj.save()

    await safe_update_settings()
    cache.delete(SETTINGS_CACHE_KEY)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

