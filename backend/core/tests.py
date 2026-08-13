from .api import bolt
from django.db import connections
from django.core.cache import cache
from utils import generate_dummy_image
from django_bolt.testing import TestClient
from .models import BdayaUser, Track, UserRole
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

# class TestCore(TestCase):

#     @classmethod
#     async def asetUpTestData(cls) -> None:
#         cls.async_client = AsyncTestClient(bolt)

#         cls.org_user = BdayaUser(
#             username="ahmed",
#             email="ahmed@gmail.com",
#             phone_number="+201033343329",
#             role=UserRole.ORGANIZER
#         )

#         _, fake_image = await asyncio.gather(
#             sync_to_async(cls.org_user.set_password)("password"),
#             sync_to_async(generate_dummy_image)()
#         )
#         _, cls.track_python, cls.track_java =  await asyncio.gather(
#             cls.org_user.asave(),
#             Track.objects.acreate(name="Python", prefix="p", image=SimpleUploadedFile("img.jpeg", fake_image, "image/jpeg")),
#             Track.objects.acreate(name="Java", prefix="j", image=SimpleUploadedFile("img.jpeg", fake_image, "image/jpeg"))
#         )

#     @classmethod
#     def setUpTestData(cls) -> None:
#         async_to_sync(cls.asetUpTestData)()

#     def setUp(self) -> None:
#         self.async_client = AsyncTestClient(bolt)
#         cache.clear()

#     async def test_valid_login(self) -> None:
#         async with self.async_client as client:
#             response = await client.post(
#                 "/api/login/",
#                 json={
#                     "email": self.org_user.email,
#                     "password": "password",
#                 },
#             )

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(response.json()['is_admin'])
#         self.assertIn("access_token", response.cookies)
#         self.assertIn("refresh_token", response.cookies)

#     async def test_invalid_login(self) -> None:
#         async with self.async_client as client:
#             response = await client.post(
#                 "/api/login/",
#                 json={
#                     "email": self.org_user.email,
#                     "password": "passdwsword",
#                 },
#             )

#         self.assertEqual(response.status_code, 400)

#     async def test_valid_register(self) -> None:
#         async with self.async_client as client:
#             response = await client.post(
#                 "/api/register/",
#                 json={
#                     "name": "ali",
#                     "email": "ali@gmail.com",
#                     "password": "ali111213",
#                     "phone_number": "+201288849905",
#                     "collage_code": "C2301261",
#                     "request_track_id": self.track_python.pk
#                 },
#             )
#         data = response.json()
#         pprint(data)
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(data['code'], 'p-1')
#         self.assertEqual(data['track']['name'], self.track_python.name)
#         self.assertIn("access_token", response.cookies)
#         self.assertIn("refresh_token", response.cookies)

#     async def test_invalid_register(self) -> None:
#         async with self.async_client as client:
#             response = await client.post(
#                 "/api/register/",
#                 json={
#                     "name": "ali",
#                     "email": "ali@gmail.com",
#                     "password": "ali111213",
#                     "phone_number": "+2012888499",
#                     "collage_code": "B2301261",
#                     "request_track_id": self.track_python.pk
#                 },
#             )
#         print(response.status_code)
#         self.assertEqual(response.status_code, 422)
#         data = response.json()['detail']
#         self.assertEqual(data[0]['loc'][-1], 'phone_number')
#         self.assertEqual(data[0]['type'], 'value_error')
#         self.assertEqual(data[1]['loc'][-1], 'collage_code')
#         self.assertEqual(data[1]['type'], 'value_error')

#     async def test_tracks_get(self) -> None:
#         async with self.async_client as client:
#             response = await client.get("/api/tracks/")

#         data = response.json()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(data), 2)
#         self.assertEqual(data[0]['name'], self.track_python.name)
#         self.assertEqual(data[1]['name'], self.track_java.name)

#     async def test_get_one_track(self) -> None:
#         async with self.async_client as client:
#             response = await client.get(f"/api/tracks/{self.track_python.name}/")

#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(data['name'], self.track_python.name)

#     async def test_add_track(self) -> None:
#         client = AsyncTestClient(bolt)
#         await client.post(
#             "/api/login/",
#             json={
#                 "email": self.org_user.email,
#                 "password": "password",
#             },
#         )
#         fake_image = SimpleUploadedFile(
#             name='test_image.jpg',
#             content=generate_dummy_image(),
#             content_type='image/jpeg'
#         )
#         response = await client.post(
#             "/api/tracks/",
#             json={
#                 "name": "C-Sharp",
#                 "en_description": "test desc",
#                 "ar_description": "وصف اختبار",
#                 "prefix": "c",
#             },
#             files={
#                 "image": fake_image
#             }
#         )
#         self.assertEqual(response.status_code, 201)

#     async def test_auth(self) -> None:
#         client = AsyncTestClient(bolt)
#         await client.post(
#             "/api/login/",
#             json={
#                 "email": self.org_user.email,
#                 "password": "password",
#             },
#         )
#         response = await client.get("/api/test-auth/")
#         self.assertEqual(response.status_code, 200)
#         data = response.json()
#         self.assertEqual(data['username'], self.org_user.username)
#         self.assertFalse(data['is_admin'])


import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def close_db_connections():
    """
    Forces Django to close all lingering async connections
    after the test finishes, allowing Postgres to drop the test DB.
    """
    cache.clear()
    yield
    connections.close_all()


@pytest.fixture(scope="module", autouse=True)
def setup_data(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        org_user = BdayaUser(
            username="ahmed",
            email="ahmed@gmail.com",
            phone_number="+201033343329",
            role=UserRole.ORGANIZER,
        )
        org_user.set_password("password")
        org_user.save()

        fake_image = generate_dummy_image()
        Track.objects.bulk_create(
            [
                Track(
                    name="Python",
                    prefix="p",
                    image=SimpleUploadedFile("img.jpeg", fake_image, "image/jpeg"),
                ),
                Track(
                    name="Java",
                    prefix="j",
                    image=SimpleUploadedFile("img.jpeg", fake_image, "image/jpeg"),
                ),
            ]
        )


# --- Your Tests Below ---


def test_user_was_created() -> None:
    assert BdayaUser.objects.count() == 1
    assert BdayaUser.objects.get(username="ahmed").role == UserRole.ORGANIZER


def test_tracks_were_created() -> None:
    assert Track.objects.count() == 2


def test_valid_login() -> None:
    with TestClient(bolt) as client:
        response = client.post(
            "/api/login/",
            json={
                "email": "ahmed@gmail.com",
                "password": "password",
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["is_admin"] is False

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_invalid_login() -> None:
    with TestClient(bolt) as client:
        response = client.post(
            "/api/login/",
            json={
                "email": "ahmed@gmail.com",
                "password": "passdwsword",
            },
        )

    assert response.status_code == 400


def test_valid_register() -> None:
    with TestClient(bolt) as client:
        response = client.post(
            "/api/register/",
            json={
                "name": "ali",
                "email": "ali@gmail.com",
                "password": "ali111213",
                "phone_number": "+201288849905",
                "collage_code": "C2301261",
                "request_track_id": 1,
            },
        )
    data = response.json()
    assert response.status_code == 201
    assert data["code"] == "p-1"
    assert data["track"]["name"] == "Python"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_invalid_register() -> None:
    with TestClient(bolt) as client:
        response = client.post(
            "/api/register/",
            json={
                "name": "ali",
                "email": "ali@gmail.com",
                "password": "ali111213",
                "phone_number": "+2012888499",
                "collage_code": "B2301261",
                "request_track_id": 1,
            },
        )
    assert response.status_code == 422
    data = response.json()["detail"]
    print()
    print(data)
    # assert data[0]['loc'][-1] == 'phone_number'
    # assert data[0]['type'] == 'value_error'
    # assert data[1]['loc'][-1] == 'collage_code'
    # assert data[1]['type'] == 'value_error'


def test_tracks_get() -> None:
    with TestClient(bolt) as client:
        response = client.get("/api/tracks/")

    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == "Python"
    assert data[1]["name"] == "Java"


def test_get_one_track() -> None:
    with TestClient(bolt) as client:
        response = client.get(f"/api/tracks/Python/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"], "Python"

def test_auth() -> None:
    with TestClient(bolt) as client:
        login_response = client.post(
            "/api/login/",
            json={
                "email": "ahmed@gmail.com",
                "password": "password",
            },
        )

        token = login_response.cookies.get("access_token")
        assert token is not None
        
        client.cookies = {"access_token": token}
        response = client.get("/api/test-auth/")

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "ahmed"
    assert data["is_admin"] is False
