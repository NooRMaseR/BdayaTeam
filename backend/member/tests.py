import asyncio
from datetime import timedelta
# from django_bolt import status
# from django.test import TestCase
from django.utils import timezone
from django.db import connections
from django.core.cache import cache
from asgiref.sync import async_to_sync, sync_to_async
from django.core.files.uploadedfile import SimpleUploadedFile
# from django.test.client import AsyncClient, encode_multipart, BOUNDARY
from django_bolt.testing import AsyncTestClient, TestClient
from django_bolt.auth import create_jwt_for_user
from .api import bolt

from technical.models import Task
from core.models import BdayaUser, Track, UserRole
from .models import ReciviedTask, ReciviedTaskFile
from utils import JSON_CONTENT_TYPE, generate_dummy_image

# Create your tests here.

# class MemberTest(TestCase):
    
#     @classmethod
#     async def asetUpTestData(cls) -> None:
#         cls.async_client = AsyncClient()
#         cls.org_async_client = AsyncClient()
#         cls.tech_async_client = AsyncClient()
#         cls.track_python = await Track.objects.acreate(name="Python", prefix="p")
        
#         tasks = [
#             Task(
#                 task_number=i,
#                 track=cls.track_python,
#                 expires_at=timezone.now() + timedelta(days=i),
#                 description=f"test description for task {i}"
#             ) for i in range(1, 6)
#         ]
        
#         cls.fake_image = SimpleUploadedFile(
#             "image.jpeg",
#             generate_dummy_image(),
#             "image/jpeg"
#         )
        
#         await asyncio.gather(
#             Task.objects.abulk_create(tasks),
#             cls.async_client.post(
#                 "/api/register/",
#                 dict(
#                     name="John Doe",
#                     email="john@example.com",
#                     collage_code="C2302986",
#                     request_track_id=cls.track_python.pk,
#                     phone_number="+201100093367"
#                 ),
#                 content_type=JSON_CONTENT_TYPE
#             )
#         )
#         cls.user = await BdayaUser.objects.select_related('member', 'track').aget(email="john@example.com")
        
#         cls.recived_task = await ReciviedTask.objects.acreate(
#             task_id=1,
#             member=cls.user.member, # type: ignore
#             track=cls.user.track,
#             notes="no notes",
#         )
        
#         cls.tech_user = BdayaUser(
#             username="ali",
#             email="ali@gmail.com",
#             phone_number="+201188893356",
#             track=cls.track_python,
#             role=UserRole.TECHNICAL
#         )
#         cls.org_user = BdayaUser(
#             username="ahmed",
#             email="ahmed@gmail.com",
#             phone_number="+201188893756",
#             role=UserRole.ORGANIZER
#         )
        
#         await asyncio.gather(
#             ReciviedTaskFile.objects.acreate(
#                 recivied_task=cls.recived_task,
#                 file=cls.fake_image
#             ),
#             sync_to_async(cls.org_user.set_password)("password"),
#             sync_to_async(cls.tech_user.set_password)("password"),
#         )
#         await asyncio.gather(
#             cls.tech_user.asave(),
#             cls.org_user.asave(),
#         )
#         await asyncio.gather(
#             cls.tech_async_client.post(
#                 "/api/login/",
#                 {
#                     "email": cls.tech_user.email,
#                     "password": "password",
#                 },
#                 content_type=JSON_CONTENT_TYPE
#             ),
#             cls.org_async_client.post(
#                 "/api/login/",
#                 {
#                     "email": cls.org_user.email,
#                     "password": "password",
#                 },
#                 content_type=JSON_CONTENT_TYPE
#             ),
#         )
    
#     @classmethod
#     def setUpTestData(cls) -> None:
#         async_to_sync(cls.asetUpTestData)()
    
#     def setUp(self) -> None:
#         cache.clear()
        
#         refresh = RefreshToken.for_user(self.user)
#         refresh['role'] = self.user.role
#         refresh['code'] = self.user.member.code # type: ignore
        
#         self.async_client.cookies["access_token"] = str(refresh.access_token)
#         self.async_client.cookies["refresh_token"] = str(refresh)
        
        
#         refresh = RefreshToken.for_user(self.org_user)
#         refresh['role'] = self.org_user.role
        
#         self.org_async_client.cookies["access_token"] = str(refresh.access_token)
#         self.org_async_client.cookies["refresh_token"] = str(refresh)
        
        
#         refresh = RefreshToken.for_user(self.tech_user)
#         refresh['role'] = self.tech_user.role
        
#         self.tech_async_client.cookies["access_token"] = str(refresh.access_token)
#         self.tech_async_client.cookies["refresh_token"] = str(refresh)
    
#     async def test_get_all_tasks(self) -> None:
#         response = await self.async_client.get("/api/member/tasks/")
#         data = response.json()
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(data), 4)
#         self.assertEqual(max(data, key=lambda x: x['task_number'])['task_number'], 5)
#         self.assertEqual(min(data, key=lambda x: x['task_number'])['task_number'], 2)

#     async def test_submit_valid_task(self) -> None:
#         payload = {
#             "task_id": 2,
#             "files": [
#                 self.fake_image,
#                 self.fake_image,
#             ],
#             "notes": "nice ?"
#         }
#         response = await self.async_client.post("/api/member/tasks/", payload)
#         self.assertEqual(response.status_code, 201)

#     async def test_submit_invalid_task(self) -> None:
#         payload = {
#             "task_id": 6,
#             "files": [
#                 self.fake_image
#             ],
#             "notes": "nice ?"
#         }
#         response = await self.async_client.post("/api/member/tasks/", payload)
#         self.assertEqual(response.status_code, 404)
    
#     async def test_submit_dublicated_task(self) -> None:
#         payload = {
#             "task_id": 1,
#             "files": [
#                 self.fake_image
#             ],
#             "notes": "nice ?"
#         }
#         response = await self.async_client.post("/api/member/tasks/", payload)
#         self.assertEqual(response.status_code, 400)
#         self.assertIn("details", response.json())

#     async def test_get_protected_task_file(self) -> None:
#         response = await self.async_client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(response.headers.get("Content-Type"))
#         self.assertEqual(response.get("Content-Type"), 'image/jpeg')

#     async def test_get_protected_task_file_from_unuthorized(self) -> None:
#         client = AsyncClient()
#         response = await client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
#     async def test_get_protected_task_file_from_another_user(self) -> None:
#         client = AsyncClient()
#         register_response = await client.post(
#             "/api/register/",
#             {
#                 "name": "John Doe 2",
#                 "email": "john2@example.com",
#                 "collage_code": "C2301986",
#                 "request_track_id": self.track_python.pk,
#                 "phone_number": "+201200093367"
#             },
#             content_type=JSON_CONTENT_TYPE
#         )
        
#         self.assertEqual(register_response.status_code, 201)
        
#         response = await client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
#     async def test_get_protected_task_file_from_tech(self) -> None:
#         response = await self.tech_async_client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
#         self.assertEqual(response.status_code, 200)
    
#     async def test_get_protected_task_file_from_org(self) -> None:
#         response = await self.org_async_client.get(f"/api/member/protected_media/tasks/{self.recived_task.pk}/")
        
#         self.assertEqual(response.status_code, 200)
    
#     async def test_get_memeber_profile(self) -> None:
#         response = await self.async_client.get(f"/api/member/profile/{self.user.member.code}/") # type: ignore
#         data = response.json()
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['absents'], 0)
#         self.assertEqual(data['total_tasks_sent'], 1)
#         self.assertEqual(data['missing_tasks'], 4)
#         self.assertEqual(data['code'], self.user.member.code) # type: ignore
#         self.assertEqual(data['status'], "normal")
        
#     async def test_get_memeber_profile_with_invalid_code(self) -> None:
#         response = await self.async_client.get(f"/api/member/profile/pad/")
#         data = response.json()
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['absents'], 0)
#         self.assertEqual(data['total_tasks_sent'], 1)
#         self.assertEqual(data['missing_tasks'], 4)
#         self.assertEqual(data['code'], self.user.member.code) # type: ignore
#         self.assertEqual(data['status'], "normal")
        
#     async def test_get_memeber_profile_from_tech(self) -> None:
#         response = await self.tech_async_client.get(f"/api/member/profile/{self.user.member.code}/") # type: ignore
#         data = response.json()
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['absents'], 0)
#         self.assertEqual(data['total_tasks_sent'], 1)
#         self.assertEqual(data['missing_tasks'], 4)
#         self.assertEqual(data['code'], self.user.member.code) # type: ignore
#         self.assertEqual(data['status'], "normal")
    
#     async def test_get_memeber_profile_from_org(self) -> None:
#         response = await self.org_async_client.get(f"/api/member/profile/{self.user.member.code}/") # type: ignore
#         data = response.json()
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['absents'], 0)
#         self.assertEqual(data['total_tasks_sent'], 1)
#         self.assertEqual(data['missing_tasks'], 4)
#         self.assertEqual(data['code'], self.user.member.code) # type: ignore
#         self.assertEqual(data['status'], "normal")
        
#     async def test_get_editable_task(self) -> None:
#         response = await self.async_client.get(f"/api/member/edit-task/{self.recived_task.pk}/")
#         data = response.json()
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(data['files_url']), 1)
#         self.assertEqual(data['notes'], "no notes")
#         self.assertFalse(data['signed'])
#         self.assertFalse(data['task']['expired'])
        
#     async def test_edit_task(self) -> None:
#         encoded_form = encode_multipart(BOUNDARY, {
#             "notes": "okay ?"
#         })
#         response = await self.async_client.put(
#             f"/api/member/edit-task/{self.recived_task.pk}/",
#             encoded_form,
#             f"multipart/form-data; boundary={BOUNDARY}"
#         )
        
#         self.assertEqual(response.status_code, 204)
        
#         response = await self.async_client.get(f"/api/member/edit-task/{self.recived_task.pk}/")
#         data = response.json()
        
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(data['files_url']), 1)
#         self.assertEqual(data['notes'], "okay ?")

import pytest

pytestmark = pytest.mark.django_db(transaction=True)

@pytest.fixture(scope="module", autouse=True)
def member_setup(django_db_setup, django_db_blocker):
    """Sets up the database state for member tests synchronously."""
    with django_db_blocker.unblock():
        track_python = Track.objects.create(name="Python", prefix="p")
        
        tasks = [
            Task(
                task_number=i,
                track=track_python,
                expires_at=timezone.now() + timedelta(days=i),
                description=f"test description for task {i}"
            ) for i in range(1, 6)
        ]
        Task.objects.bulk_create(tasks) # No await
        
        fake_image = SimpleUploadedFile("image.jpeg", b"dummy_content", "image/jpeg")
        
        with TestClient(bolt) as client:
            client.post(
                "/api/register/",
                json={
                    "name": "John Doe",
                    "email": "john@example.com",
                    "collage_code": "C2302986",
                    "request_track_id": track_python.pk,
                    "phone_number": "+201100093367"
                }
            )
            
        user = BdayaUser.objects.select_related('member', 'track').get(email="john@example.com")
        
        recived_task = ReciviedTask.objects.create(
            task_id=1,
            member=user.member,
            track=user.track,
            notes="no notes",
        )
        
        ReciviedTaskFile.objects.create(recivied_task=recived_task, file=fake_image)
        
        tech_user = BdayaUser.objects.create(
            username="ali",
            email="ali@gmail.com",
            phone_number="+201188893356",
            track=track_python,
            role=UserRole.TECHNICAL
        )
        # Standard synchronous password setting
        tech_user.set_password("password")
        tech_user.save()
        
        org_user = BdayaUser.objects.create(
            username="ahmed",
            email="ahmed@gmail.com",
            phone_number="+201188893756",
            role=UserRole.ORGANIZER
        )
        org_user.set_password("password")
        org_user.save()

@pytest.fixture
def get_login_cookies():
    """
    Simulates a real HTTP login request and returns the response cookies.
    Assumes the user's password was set to 'password' during setup.
    """
    def _login(email: str, password: str):
        with TestClient(bolt) as auth_client:
            response = auth_client.post(
                "/api/login/",
                json={
                    "email": email,
                    "password": password,
                }
            )
            
            # Ensure the login actually succeeded before running the test
            assert response.status_code == 200, f"Login failed for {email}"
            
            # Return the cookies dictionary attached to the response
            return response.cookies
            
    return _login

# --- Tests ---

def test_get_all_tasks(get_login_cookies):
    cookies = get_login_cookies("john@example.com", "p-1@C2302986")
    with TestClient(bolt) as client:
        response = client.get("/api/member/tasks/", cookies=cookies)
        
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert max(data, key=lambda x: x['task_number'])['task_number'] == 5
    assert min(data, key=lambda x: x['task_number'])['task_number'] == 2

# async def test_submit_valid_task(auth_cookies):
#     cookies = auth_cookies(member_setup["user"])
    
#     # Use tuples for multi-file uploads with the same key
#     files = [
#         ("files", member_setup["fake_image"]),
#         ("files", member_setup["fake_image"]),
#     ]
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.post(
#             "/api/member/tasks/", 
#             data={"task_id": 2, "notes": "nice ?"},
#             files=files,
#             cookies=cookies
#         )
        
#     assert response.status_code == 201

# async def test_submit_invalid_task(auth_cookies):
#     cookies = auth_cookies(member_setup["user"])
#     files = [("files", member_setup["fake_image"])]
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.post(
#             "/api/member/tasks/", 
#             data={"task_id": 6, "notes": "nice ?"},
#             files=files,
#             cookies=cookies
#         )
        
#     assert response.status_code == 404
    
# async def test_submit_dublicated_task(auth_cookies):
#     cookies = auth_cookies(member_setup["user"])
#     files = [("files", member_setup["fake_image"])]
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.post(
#             "/api/member/tasks/", 
#             data={"task_id": 1, "notes": "nice ?"},
#             files=files,
#             cookies=cookies
#         )
        
#     assert response.status_code == 400
#     assert "details" in response.json()

# async def test_get_protected_task_file(auth_cookies):
#     cookies = auth_cookies(member_setup["user"])
#     task_id = member_setup["recived_task"].pk
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.get(f"/api/member/protected_media/tasks/{task_id}/", cookies=cookies)
        
#     assert response.status_code == 200
#     assert response.headers.get("Content-Type") == 'image/jpeg'

# async def test_get_protected_task_file_from_unuthorized(member_setup):
#     task_id = member_setup["recived_task"].pk
    
#     async with AsyncTestClient(bolt) as client:
#         # No cookies passed!
#         response = await client.get(f"/api/member/protected_media/tasks/{task_id}/")
        
#     assert response.status_code == 401
    
# async def test_get_protected_task_file_from_another_user(auth_cookies):
#     task_id = member_setup["recived_task"].pk
#     track = member_setup["track"]
    
#     async with AsyncTestClient(bolt) as client:
#         register_response = await client.post(
#             "/api/register/",
#             json={
#                 "name": "John Doe 2",
#                 "email": "john2@example.com",
#                 "collage_code": "C2301986",
#                 "request_track_id": track.pk,
#                 "phone_number": "+201200093367"
#             }
#         )
#         assert register_response.status_code == 201
        
#         # Authenticate as the newly created user
#         new_user = await BdayaUser.objects.aget(email="john2@example.com")
#         cookies = auth_cookies(new_user)
        
#         response = await client.get(f"/api/member/protected_media/tasks/{task_id}/", cookies=cookies)
        
#     assert response.status_code == 404
    
# async def test_get_protected_task_file_from_tech(auth_cookies):
#     cookies = auth_cookies(member_setup["tech_user"])
#     task_id = member_setup["recived_task"].pk
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.get(f"/api/member/protected_media/tasks/{task_id}/", cookies=cookies)
        
#     assert response.status_code == 200
    
# async def test_get_protected_task_file_from_org(auth_cookies):
#     cookies = auth_cookies(member_setup["org_user"])
#     task_id = member_setup["recived_task"].pk
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.get(f"/api/member/protected_media/tasks/{task_id}/", cookies=cookies)
        
#     assert response.status_code == 200
    
# async def test_get_memeber_profile(auth_cookies):
#     cookies = auth_cookies(member_setup["user"])
#     code = member_setup["user"].member.code
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.get(f"/api/member/profile/{code}/", cookies=cookies)
        
#     assert response.status_code == 200
#     data = response.json()
#     assert data['absents'] == 0
#     assert data['total_tasks_sent'] == 1
#     assert data['missing_tasks'] == 4
#     assert data['code'] == code
#     assert data['status'] == "normal"
        
# async def test_get_memeber_profile_with_invalid_code(auth_cookies):
#     cookies = auth_cookies(member_setup["user"])
#     code = member_setup["user"].member.code
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.get("/api/member/profile/pad/", cookies=cookies)
        
#     assert response.status_code == 200
#     data = response.json()
#     assert data['code'] == code
#     assert data['status'] == "normal"
        
# async def test_get_memeber_profile_from_tech(auth_cookies):
#     cookies = auth_cookies(member_setup["tech_user"])
#     code = member_setup["user"].member.code
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.get(f"/api/member/profile/{code}/", cookies=cookies)
        
#     assert response.status_code == 200
#     data = response.json()
#     assert data['code'] == code
    
# async def test_get_memeber_profile_from_org(auth_cookies):
#     cookies = auth_cookies(member_setup["org_user"])
#     code = member_setup["user"].member.code
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.get(f"/api/member/profile/{code}/", cookies=cookies)
        
#     assert response.status_code == 200
#     data = response.json()
#     assert data['code'] == code
        
# async def test_get_editable_task(auth_cookies):
#     cookies = auth_cookies(member_setup["user"])
#     task_id = member_setup["recived_task"].pk
    
#     async with AsyncTestClient(bolt) as client:
#         response = await client.get(f"/api/member/edit-task/{task_id}/", cookies=cookies)
        
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data['files_url']) == 1
#     assert data['notes'] == "no notes"
#     assert data['signed'] is False
#     assert data['task']['expired'] is False
        
# async def test_edit_task(auth_cookies):
#     cookies = auth_cookies(member_setup["user"])
#     task_id = member_setup["recived_task"].pk
    
#     async with AsyncTestClient(bolt) as client:
#         # Standard put request with data dictionary handles multipart boundaries automatically
#         response = await client.put(
#             f"/api/member/edit-task/{task_id}/",
#             data={"notes": "okay ?"},
#             cookies=cookies
#         )
#         assert response.status_code == 204
        
#         # Verify changes
#         verify_response = await client.get(f"/api/member/edit-task/{task_id}/", cookies=cookies)
        
#     assert verify_response.status_code == 200
#     data = verify_response.json()
#     assert len(data['files_url']) == 1
#     assert data['notes'] == "okay ?"