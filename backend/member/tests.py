import asyncio
from datetime import timedelta
from ninja_extra import status
from django.test import TestCase
from django.utils import timezone
from django.core.cache import cache
from asgiref.sync import async_to_sync, sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import AsyncClient, encode_multipart, BOUNDARY

from technical.models import Task
from core.models import BdayaUser, Track, UserRole
from .models import ReciviedTask, ReciviedTaskFile
from utils import JSON_CONTENT_TYPE, generate_dummy_image

# Create your tests here.

class MemberTest(TestCase):
    
    @classmethod
    async def asetUpTestData(cls) -> None:
        cls.async_client = AsyncClient()
        cls.org_async_client = AsyncClient()
        cls.tech_async_client = AsyncClient()
        cls.track_python = await Track.objects.acreate(name="Python", prefix="p")
        
        tasks = [
            Task(
                task_number=i,
                track=cls.track_python,
                expires_at=timezone.now() + timedelta(days=i),
                description=f"test description for task {i}"
            ) for i in range(1, 6)
        ]
        
        cls.fake_image = SimpleUploadedFile(
            "image.jpeg",
            generate_dummy_image(),
            "image/jpeg"
        )
        
        await asyncio.gather(
            Task.objects.abulk_create(tasks),
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
        cls.user = await BdayaUser.objects.select_related('member', 'track').aget(email="john@example.com")
        
        cls.recived_task = await ReciviedTask.objects.acreate(
            task_id=1,
            member=cls.user.member, # type: ignore
            track=cls.user.track,
            notes="no notes",
        )
        
        cls.tech_user = BdayaUser(
            username="ali",
            email="ali@gmail.com",
            phone_number="+201188893356",
            track=cls.track_python,
            role=UserRole.TECHNICAL
        )
        cls.org_user = BdayaUser(
            username="ahmed",
            email="ahmed@gmail.com",
            phone_number="+201188893756",
            role=UserRole.ORGANIZER
        )
        
        await asyncio.gather(
            ReciviedTaskFile.objects.acreate(
                recivied_task=cls.recived_task,
                file=cls.fake_image
            ),
            sync_to_async(cls.org_user.set_password)("password"),
            sync_to_async(cls.tech_user.set_password)("password"),
        )
        await asyncio.gather(
            cls.tech_user.asave(),
            cls.org_user.asave(),
        )
        await asyncio.gather(
            cls.tech_async_client.post(
                "/api/login/",
                {
                    "email": cls.tech_user.email,
                    "password": "password",
                },
                content_type=JSON_CONTENT_TYPE
            ),
            cls.org_async_client.post(
                "/api/login/",
                {
                    "email": cls.org_user.email,
                    "password": "password",
                },
                content_type=JSON_CONTENT_TYPE
            ),
        )
    
    @classmethod
    def setUpTestData(cls) -> None:
        async_to_sync(cls.asetUpTestData)()
    
    def setUp(self) -> None:
        cache.clear()
        
        refresh = RefreshToken.for_user(self.user)
        refresh['role'] = self.user.role
        refresh['code'] = self.user.member.code # type: ignore
        
        self.async_client.cookies["access_token"] = str(refresh.access_token)
        self.async_client.cookies["refresh_token"] = str(refresh)
        
        
        refresh = RefreshToken.for_user(self.org_user)
        refresh['role'] = self.org_user.role
        
        self.org_async_client.cookies["access_token"] = str(refresh.access_token)
        self.org_async_client.cookies["refresh_token"] = str(refresh)
        
        
        refresh = RefreshToken.for_user(self.tech_user)
        refresh['role'] = self.tech_user.role
        
        self.tech_async_client.cookies["access_token"] = str(refresh.access_token)
        self.tech_async_client.cookies["refresh_token"] = str(refresh)
    
    async def test_get_all_tasks(self) -> None:
        response = await self.async_client.get("/api/member/tasks/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 4)
        self.assertEqual(max(data, key=lambda x: x['task_number'])['task_number'], 5)
        self.assertEqual(min(data, key=lambda x: x['task_number'])['task_number'], 2)

    async def test_submit_valid_task(self) -> None:
        payload = {
            "task_id": 2,
            "files": [
                self.fake_image,
                self.fake_image,
            ],
            "notes": "nice ?"
        }
        response = await self.async_client.post("/api/member/tasks/", payload)
        self.assertEqual(response.status_code, 201)

    async def test_submit_invalid_task(self) -> None:
        payload = {
            "task_id": 6,
            "files": [
                self.fake_image
            ],
            "notes": "nice ?"
        }
        response = await self.async_client.post("/api/member/tasks/", payload)
        self.assertEqual(response.status_code, 404)
    
    async def test_submit_dublicated_task(self) -> None:
        payload = {
            "task_id": 1,
            "files": [
                self.fake_image
            ],
            "notes": "nice ?"
        }
        response = await self.async_client.post("/api/member/tasks/", payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("details", response.json())

    async def test_get_protected_task_file(self) -> None:
        response = await self.async_client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers.get("Content-Type"))
        self.assertEqual(response.get("Content-Type"), 'image/jpeg')

    async def test_get_protected_task_file_from_unuthorized(self) -> None:
        client = AsyncClient()
        response = await client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    async def test_get_protected_task_file_from_another_user(self) -> None:
        client = AsyncClient()
        register_response = await client.post(
            "/api/register/",
            {
                "name": "John Doe 2",
                "email": "john2@example.com",
                "collage_code": "C2301986",
                "request_track_id": self.track_python.pk,
                "phone_number": "+201200093367"
            },
            content_type=JSON_CONTENT_TYPE
        )
        
        self.assertEqual(register_response.status_code, 201)
        
        response = await client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    async def test_get_protected_task_file_from_tech(self) -> None:
        response = await self.tech_async_client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
        self.assertEqual(response.status_code, 200)
    
    async def test_get_protected_task_file_from_org(self) -> None:
        response = await self.org_async_client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
        self.assertEqual(response.status_code, 200)
    
    async def test_get_memeber_profile(self) -> None:
        response = await self.async_client.get(f"/api/member/profile/{self.user.member.code}/") # type: ignore
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['absents'], 0)
        self.assertEqual(data['total_tasks_sent'], 1)
        self.assertEqual(data['missing_tasks'], 4)
        self.assertEqual(data['code'], self.user.member.code) # type: ignore
        self.assertEqual(data['status'], "normal")
        
    async def test_get_memeber_profile_with_invalid_code(self) -> None:
        response = await self.async_client.get(f"/api/member/profile/pad/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['absents'], 0)
        self.assertEqual(data['total_tasks_sent'], 1)
        self.assertEqual(data['missing_tasks'], 4)
        self.assertEqual(data['code'], self.user.member.code) # type: ignore
        self.assertEqual(data['status'], "normal")
        
    async def test_get_memeber_profile_from_tech(self) -> None:
        response = await self.tech_async_client.get(f"/api/member/profile/{self.user.member.code}/") # type: ignore
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['absents'], 0)
        self.assertEqual(data['total_tasks_sent'], 1)
        self.assertEqual(data['missing_tasks'], 4)
        self.assertEqual(data['code'], self.user.member.code) # type: ignore
        self.assertEqual(data['status'], "normal")
    
    async def test_get_memeber_profile_from_org(self) -> None:
        response = await self.org_async_client.get(f"/api/member/profile/{self.user.member.code}/") # type: ignore
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['absents'], 0)
        self.assertEqual(data['total_tasks_sent'], 1)
        self.assertEqual(data['missing_tasks'], 4)
        self.assertEqual(data['code'], self.user.member.code) # type: ignore
        self.assertEqual(data['status'], "normal")
        
    async def test_get_editable_task(self) -> None:
        response = await self.async_client.get(f"/api/member/edit-task/{self.recived_task.pk}/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['files_url']), 1)
        self.assertEqual(data['notes'], "no notes")
        self.assertFalse(data['signed'])
        self.assertFalse(data['task']['expired'])
        
    async def test_edit_task(self) -> None:
        encoded_form = encode_multipart(BOUNDARY, {
            "notes": "okay ?"
        })
        response = await self.async_client.put(
            f"/api/member/edit-task/{self.recived_task.pk}/",
            encoded_form,
            f"multipart/form-data; boundary={BOUNDARY}"
        )
        
        self.assertEqual(response.status_code, 204)
        
        response = await self.async_client.get(f"/api/member/edit-task/{self.recived_task.pk}/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['files_url']), 1)
        self.assertEqual(data['notes'], "okay ?")

