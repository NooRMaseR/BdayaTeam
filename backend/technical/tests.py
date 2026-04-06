import asyncio
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from django.test.client import AsyncClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import BdayaUser, Track, UserRole
from asgiref.sync import sync_to_async, async_to_sync

from technical.models import Task
from utils import JSON_CONTENT_TYPE, generate_dummy_image


# Create your tests here.

class TestTechnical(TestCase):
    
    @classmethod
    async def asetUpTestData(cls) -> None:
        cls.async_client = AsyncClient()
        cls.tech_client = AsyncClient()
        cls.member_client = AsyncClient()
        
        cls.track_python, cls.track_java = await asyncio.gather(
            Track.objects.acreate(name="Python", prefix="p"),
            Track.objects.acreate(name="Java", prefix="j"),
        )
        
        cls.tech_user = BdayaUser(
            username="ahmed",
            role=UserRole.TECHNICAL,
            phone_number="+201088876690",
            email="ahmed@gmail.com",
            track=cls.track_python
        )
        
        await sync_to_async(cls.tech_user.set_password)("password")
        
        tasks = [
            Task(
                task_number=i,
                track=cls.track_python,
                expires_at=timezone.now() + timedelta(days=i),
                description=f"test description for task {i}"
            ) for i in range(1, 6)
        ]
        
        *_, cls.created_tasks = await asyncio.gather(
            cls.tech_user.asave(),
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
            ),
            cls.async_client.post(
                "/api/register/",
                dict(
                    name="nader Doe",
                    email="nader@example.com",
                    collage_code="C2312986",
                    request_track_id=cls.track_python.pk,
                    phone_number="+201200093367"
                ),
                content_type=JSON_CONTENT_TYPE
            ),
            cls.async_client.post(
                "/api/register/",
                dict(
                    name="james Doe",
                    email="james@example.com",
                    collage_code="C2302976",
                    request_track_id=cls.track_python.pk,
                    phone_number="+201100093377"
                ),
                content_type=JSON_CONTENT_TYPE
            ),
            Task.objects.abulk_create(tasks),
        )
        
        cls.member_user = await BdayaUser.objects.aget(email="john@example.com")

        cls.fake_image = SimpleUploadedFile(
            "image.jpeg",
            generate_dummy_image(),
            "image/jpeg"
        )
        
        await cls.member_client.post(
            "/api/login/",
            {"email": "john@example.com", "password": "password"},
            JSON_CONTENT_TYPE
        )
        
        payload = {
            "task_id": 2,
            "files": [
                cls.fake_image,
                cls.fake_image,
            ],
            "notes": "nice ?"
        }
        await cls.member_client.post("/api/member/tasks/", payload)
    
    @classmethod
    def setUpTestData(cls) -> None:
        async_to_sync(cls.asetUpTestData)()
        
    def setUp(self) -> None:
        cache.clear()
        
        refresh = RefreshToken.for_user(self.member_user)
        refresh['role'] = self.member_user.role
        refresh['code'] = self.member_user.member.code # type: ignore
        
        self.member_client.cookies["access_token"] = str(refresh.access_token)
        self.member_client.cookies["refresh_token"] = str(refresh)
        
        
        refresh = RefreshToken.for_user(self.tech_user)
        refresh['role'] = self.tech_user.role
        
        self.tech_client.cookies["access_token"] = str(refresh.access_token)
        self.tech_client.cookies["refresh_token"] = str(refresh)
        
    async def test_get_all_tasks(self) -> None:
        response = await self.tech_client.get("/api/technical/tasks/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 5)
        self.assertEqual(max(data, key= lambda x: x['task_number'])['task_number'], 5)
        self.assertEqual(min(data, key= lambda x: x['task_number'])['task_number'], 1)

    async def test_member_get_all_tasks(self) -> None:
        response = await self.member_client.get("/api/technical/tasks/")
        data = response.json()
        
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(data, {"detail": 'Only technicals are Allowed'})
        
    async def test_add_task(self) -> None:
        response = await self.tech_client.post(
            "/api/technical/tasks/",
            {
                "task_number": 6,
                "expires_at": timezone.now() + timedelta(days=1),
                "description": "a task"
            },
            JSON_CONTENT_TYPE
        )
        
        self.assertEqual(response.status_code, 201)
        
    async def test_add_dublicated_task(self) -> None:
        response = await self.tech_client.post(
            "/api/technical/tasks/",
            {
                "task_number": 5,
                "expires_at": timezone.now() + timedelta(days=1),
                "description": "a task"
            },
            JSON_CONTENT_TYPE
        )
        data = response.json()
        
        self.assertEqual(response.status_code, 400)
        self.assertTrue(data.get('task_number'))
        self.assertEqual(data['task_number'], "This task number already exists")
        
    async def test_add_invalid_past_date_task(self) -> None:
        response = await self.tech_client.post(
            "/api/technical/tasks/",
            {
                "task_number": 6,
                "expires_at": timezone.now() - timedelta(days=1),
                "description": "a task"
            },
            JSON_CONTENT_TYPE
        )
        data = response.json()
        
        self.assertEqual(response.status_code, 422)
        self.assertTrue(data.get('detail'))
        self.assertEqual(data['detail'][0]['ctx']['error'], "expires_at cannot be in the past")
    
    async def test_get_one_task(self) -> None:
        response = await self.tech_client.get(f"/api/technical/tasks/{self.created_tasks[0].pk}/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['expired'])
        self.assertEqual(data['task_number'], 1)
        
    async def test_update_task(self) -> None:
        response = await self.tech_client.put(
            f"/api/technical/tasks/{self.created_tasks[1].pk}/",
            {
                "task_number": self.created_tasks[1].task_number,
                "expires_at": timezone.now() + timedelta(days=1),
                "description": "a task update"
            },
            JSON_CONTENT_TYPE
        )
        
        self.assertEqual(response.status_code, 204)
        check_response = await self.tech_client.get(f"/api/technical/tasks/{self.created_tasks[1].pk}/")
        data = check_response.json()
        
        self.assertEqual(check_response.status_code, 200)
        self.assertEqual(data['description'], "a task update")

    async def test_delete_nonexistent_task(self) -> None:
        response = await self.tech_client.delete("/api/technical/tasks/9999/")
        self.assertEqual(response.status_code, 404)

    async def test_get_members_with_tasks(self) -> None:
        response = await self.tech_client.get(f"/api/technical/members/Python/with-tasks/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 3)

    async def test_get_members_wrong_track_forbidden(self) -> None:
        response = await self.tech_client.get(f"/api/technical/members/Java/with-tasks/")
        
        self.assertEqual(response.status_code, 403)
        self.assertIn("details", response.json())
