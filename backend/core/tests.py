import asyncio
from django.test import TestCase
from django.core.cache import cache
from django.test.client import AsyncClient
from .models import BdayaUser, Track, UserRole
from asgiref.sync import async_to_sync, sync_to_async
from utils import JSON_CONTENT_TYPE, generate_dummy_image
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

class TestCore(TestCase):
    
    @classmethod
    async def asetUpTestData(cls) -> None:
        cls.async_client = AsyncClient()
        
        cls.org_user = BdayaUser(
            username="ahmed",
            email="ahmed@gmail.com",
            phone_number="+201033343329",
            role=UserRole.ORGANIZER
        )
        
        _, fake_image = await asyncio.gather(
            sync_to_async(cls.org_user.set_password)("password"),
            sync_to_async(generate_dummy_image)()
        )
        _, cls.track_python, cls.track_java =  await asyncio.gather(
            cls.org_user.asave(),
            Track.objects.acreate(name="Python", prefix="p", image=SimpleUploadedFile("img.jpeg", fake_image, "image/jpeg")),
            Track.objects.acreate(name="Java", prefix="j", image=SimpleUploadedFile("img.jpeg", fake_image, "image/jpeg"))
        )
        
    @classmethod
    def setUpTestData(cls) -> None:
        async_to_sync(cls.asetUpTestData)()
    
    def setUp(self) -> None:
        self.async_client = AsyncClient()
        cache.clear()
        
    async def test_valid_login(self) -> None:
        response = await self.async_client.post(
            "/api/login/",
            data={
                "email": self.org_user.email,
                "password": "password",
            },
            content_type=JSON_CONTENT_TYPE
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_admin'])
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        
    async def test_invalid_login(self) -> None:
        response = await self.async_client.post(
            "/api/login/",
            data={
                "email": self.org_user.email,
                "password": "passdwsword",
            },
            content_type=JSON_CONTENT_TYPE
        )
        
        self.assertEqual(response.status_code, 400)
        
    async def test_valid_register(self) -> None:
        response = await self.async_client.post(
            "/api/register/",
            data={
                "name": "ali",
                "email": "ali@gmail.com",
                "password": "ali111213",
                "phone_number": "+201288849905",
                "collage_code": "C2301261",
                "request_track_id": self.track_python.pk
            },
            content_type=JSON_CONTENT_TYPE
        )
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['code'], 'p-1')
        self.assertEqual(data['track']['name'], self.track_python.name)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
    
    async def test_invalid_register(self) -> None:
        response = await self.async_client.post(
            "/api/register/",
            data={
                "name": "ali",
                "email": "ali@gmail.com",
                "password": "ali111213",
                "phone_number": "+2012888499",
                "collage_code": "B2301261",
                "request_track_id": self.track_python.pk
            },
            content_type=JSON_CONTENT_TYPE
        )
        data = response.json()['detail']
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data[0]['loc'][-1], 'phone_number')
        self.assertEqual(data[0]['type'], 'value_error')
        self.assertEqual(data[1]['loc'][-1], 'collage_code')
        self.assertEqual(data[1]['type'], 'value_error')
    
    async def test_tracks_get(self) -> None:
        response = await self.async_client.get("/api/tracks/")
        data = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], self.track_python.name)
        self.assertEqual(data[1]['name'], self.track_java.name)
    
    async def test_get_one_track(self) -> None:
        response = await self.async_client.get("/api/tracks/Python/")
        
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['name'], "Python")

    async def test_add_track(self) -> None:
        client = AsyncClient()
        await client.post(
            "/api/login/",
            data={
                "email": self.org_user.email,
                "password": "password",
            },
            content_type=JSON_CONTENT_TYPE
        )
        fake_image = SimpleUploadedFile(
            name='test_image.jpg', 
            content=generate_dummy_image(),
            content_type='image/jpeg'
        )
        response = await client.post(
            "/api/tracks/",
            data={
                "name": "C-Sharp",
                "en_description": "test desc",
                "ar_description": "وصف اختبار",
                "prefix": "c",
                "image": fake_image
            }
        )
        self.assertEqual(response.status_code, 201)

    async def test_auth(self) -> None:
        client = AsyncClient()
        await client.post(
            "/api/login/",
            data={
                "email": self.org_user.email,
                "password": "password",
            },
            content_type=JSON_CONTENT_TYPE
        )
        response = await client.get(
            "/api/test-auth/",
            content_type=JSON_CONTENT_TYPE
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], self.org_user.username)
        self.assertFalse(data['is_admin'])
