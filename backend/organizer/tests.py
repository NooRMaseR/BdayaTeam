import asyncio
from ninja_extra import status
from django.test import TestCase
from django.core.cache import cache
from django.test.client import AsyncClient
from rest_framework_simplejwt.tokens import RefreshToken

from member.models import Member
from core.models import Track, BdayaUser, UserRole

from utils import JSON_CONTENT_TYPE
from asgiref.sync import async_to_sync, sync_to_async
from .models import Attendance, AttendanceStatus, AttendanceAllowedDay, MemberEditType, SiteSetting


class OrganizerAPITests(TestCase):
    
    @classmethod
    async def asetUpTestData(cls) -> None:
        cls.user = BdayaUser(
            username="ahmed",
            role=UserRole.ORGANIZER,
            phone_number="+201088876690",
            email="ahmed@gmail.com"
        )
        
        await sync_to_async(cls.user.set_password)("password")
        
        cls.async_client = AsyncClient()
        
        _, cls.track_python, cls.track_java = await asyncio.gather(
            cls.user.asave(),
            Track.objects.acreate(name="Python", prefix="p"),
            Track.objects.acreate(name="Java", prefix="j"),
        )
        
        cls.settings_data = await sync_to_async(SiteSetting.get_solo)()
        cls.settings_data.organizer_can_edit = ["bonus", "track"]
        cls.allowed_day, *_ = await asyncio.gather(
            AttendanceAllowedDay.objects.acreate(
                day="2026-02-02", 
                track=cls.track_python
            ),
            cls.settings_data.asave(),
            cls.async_client.post(
                "/api/register/",
                dict(
                    name="John Doe",
                    email="john@example.com",
                    collage_code="C2302986",
                    request_track_id=cls.track_python.pk,
                    phone_number="+201100093367"
                ),
                content_type=JSON_CONTENT_TYPE
            )
        )
        
    @classmethod
    def setUpTestData(cls) -> None:
        async_to_sync(cls.asetUpTestData)()
        
    def setUp(self) -> None:
        self.async_client = AsyncClient()
        cache.clear()
        
        refresh = RefreshToken.for_user(self.user)
        refresh['role'] = self.user.role
        
        self.async_client.cookies["access_token"] = str(refresh.access_token)
        self.async_client.cookies["refresh_token"] = str(refresh)
        
    async def test_get_members_by_track(self) -> None:
        response = await self.async_client.get("/api/organizer/members/Python/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1) # type: ignore
        self.assertEqual(data[0]['code'], "p-1") # type: ignore

    async def test_update_valid_member_data(self) -> None:
        """Test updating a simple field via MemberEditType.DATA"""
        data = {
            "code": "p-1",
            "field": "bonus",
            "value": 5,
            "type": MemberEditType.DATA
        }
        response = await self.async_client.post(
            "/api/organizer/members/Python/", 
            data, 
            content_type=JSON_CONTENT_TYPE
        )
        self.assertEqual(response.status_code, 200)
    
    async def test_update_not_allowed_field(self) -> None:
        """Test updating an invalid simple field"""
        
        data = {
            "code": "p-1",
            "field": "name",
            "value": "james",
            "type": MemberEditType.DATA
        }
        response = await self.async_client.post(
            "/api/organizer/members/Python/", 
            data, 
            content_type=JSON_CONTENT_TYPE
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json(), {"details": "field name is not allowed"})
    
    async def test_update_invalid_member_data(self) -> None:
        """Test updating a unknown member"""
        
        data = {
            "code": "p-6",
            "field": "name",
            "value": "james",
            "type": MemberEditType.DATA
        }
        response = await self.async_client.post(
            "/api/organizer/members/Python/", 
            data, 
            content_type=JSON_CONTENT_TYPE
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.json(), {"detail": "Not Found"})

    async def test_create_attendance_record(self) -> None:
        """Test creating a new attendance record via MemberEditType.ATTENDANCE"""
        
        data = {
            "code": "p-1",
            "field": "2026-02-02",
            "value": AttendanceStatus.PRESENT,
            "type": MemberEditType.ATTENDANCE
        }
        response = await self.async_client.post("/api/organizer/members/Python/", data, content_type=JSON_CONTENT_TYPE)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(await Attendance.objects.filter(member_id='p-1', status=AttendanceStatus.PRESENT).aexists())

    async def test_move_member_to_another_track(self) -> None:
        """Test the move_member_to_another_track logic"""
        data = {
            "code": "p-1",
            "field": "track",
            "value": "Java",
            "type": MemberEditType.DATA
        }
        response = await self.async_client.post("/api/organizer/members/Python/", data, JSON_CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertFalse(await Member.objects.filter(code="p-1", track__name="Python").aexists())
        self.assertTrue(await Member.objects.filter(code="j-1", track__name="Java").aexists())

    async def test_get_attendance_days(self) -> None:
        response = await self.async_client.get("/api/organizer/attendance/Python/days/")
        data = response.json()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['day'], "2026-02-02")

    async def test_create_attendance_day(self) -> None:
        data = {"day": "2026-03-03"}
        response = await self.async_client.post("/api/organizer/attendance/Python/days/", data, JSON_CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(await AttendanceAllowedDay.objects.filter(day="2026-03-03").aexists())

    async def test_create_duplicate_attendance_day(self) -> None:
        data = {"day": "2026-02-02"}
        response = await self.async_client.post("/api/organizer/attendance/Python/days/", data, JSON_CONTENT_TYPE)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", response.json()['details'])
        