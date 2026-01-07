from django.urls import reverse
from member.models import Member
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Track, BdayaUser, UserRole
from .models import Attendance, AttendanceStatus, AttendanceAllowedDay, MemberEditType


class OrganizerAPITests(APITestCase):

    def setUp(self):
        # 1. Create a user and authenticate (ensure they pass IsOrganizer)
        self.user = BdayaUser(username="ahmed", role=UserRole.ORGANIZER, phone_number="+201088876690", email="ahmed@gmail.com")
        self.user.set_password("password")
        self.user.save()
        # If IsOrganizer checks a specific attribute, set it here. 
        # For example: self.user.is_staff = True; self.user.save()
        self.client.force_authenticate(user=self.user)

        # 2. Setup initial data
        self.track_python = Track.objects.create(track="Python", prefix="p")
        self.track_java = Track.objects.create(track="Java", prefix="j")
        
        self.member = Member.objects.create(
            name="John Doe",
            email="john@example.com",
            code="p-1",
            collage_code="C2302986",
            track=self.track_python,
            phone_number="+201100093367"
        )
        
        self.allowed_day = AttendanceAllowedDay.objects.create(
            day="2026-02-02", 
            track=self.track_python
        )

    ## --- Tests for Members View --- ##

    def test_get_members_by_track(self):
        url = reverse('members-list', kwargs={'track_name': 'Python'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], "p-1")

    ## --- Tests for MemberEdit View --- ##

    def test_update_member_bonus_data(self):
        """Test updating a simple field via MemberEditType.DATA"""
        url = reverse('attendance-editor', kwargs={'track_name': 'Python'})
        data = {
            "code": "p-1",
            "field": "bonus",
            "value": 5,
            "type": MemberEditType.DATA
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.member.refresh_from_db()
        self.assertEqual(self.member.bonus, 5)

    def test_create_attendance_record(self):
        """Test creating a new attendance record via MemberEditType.ATTENDANCE"""
        url = reverse('attendance-editor', kwargs={'track_name': 'Python'})
        data = {
            "code": "p-1",
            "field": "2026-02-02",
            "value": AttendanceStatus.PRESENT.value,
            "type": MemberEditType.ATTENDANCE.value
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Attendance.objects.filter(member=self.member, status=AttendanceStatus.PRESENT).exists())

    def test_move_member_to_another_track(self):
        """Test the move_member_to_another_track logic"""
        url = reverse('attendance-editor', kwargs={'track_name': 'Python'})
        data = {
            "code": "p-1",
            "field": "track",
            "value": "Java",
            "type": MemberEditType.DATA
        }
        # Note: This test will fail if RegisterSerializer has required fields 
        # not present in your Member model (like collage_code).
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if member exists in the new track (it will have a new ID since you delete/create)
        self.assertFalse(Member.objects.filter(code="p-1", track__track="Python").exists())
        self.assertTrue(Member.objects.filter(code="j-1", track__track="Java").exists())

    ## --- Tests for AttendanceDayApi View --- ##

    def test_get_attendance_days(self):
        url = reverse('attendance-days', kwargs={'track_name': 'Python'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['day'], "2026-02-02")

    def test_create_attendance_day(self):
        url = reverse('attendance-days', kwargs={'track_name': 'Python'})
        data = {"day": "2026-03-03"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AttendanceAllowedDay.objects.filter(day="2026-03-03").exists())

    def test_create_duplicate_attendance_day_fails(self):
        url = reverse('attendance-days', kwargs={'track_name': 'Python'})
        data = {"day": "2026-02-02"} # Already exists in setUp
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists", response.data['details'])