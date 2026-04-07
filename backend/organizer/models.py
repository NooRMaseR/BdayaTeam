from enum import StrEnum
from django.db import models
from member.models import Member
from solo.models import SingletonModel
from core.models import BdayaUser, Track
from imagekit.models import ProcessedImageField
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class MemberEditType(StrEnum):
    ATTENDANCE = "attendance"
    DATA = "data"

class AttendanceStatus(models.TextChoices):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"

class AttendanceAllowedDay(models.Model):
    day = models.DateField()
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="days")
    
    class Meta:
        ordering = ("track", "day")
        unique_together = ("track", "day")
        
    def __str__(self) -> str:
        return f"{self.day} - {self.day.strftime("%A")} - {self.track}"


class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    date = models.ForeignKey(AttendanceAllowedDay, on_delete=models.CASCADE, related_name="members_attendance")
    status = models.CharField(max_length=9, choices=AttendanceStatus)
    excuse_reason = models.TextField(blank=True, null=True)
    by = models.ForeignKey(BdayaUser, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ("member", "date")
    
    def __str__(self) -> str:
        return f"{self.member.name}"

class OrganizerEditableFields(models.TextChoices):
    NAME = "name"
    STATUS = "status"
    TRACK = "track"
    BONUS = "bonus"
    EMAIL = "email"
    PHONE = "phone"

class SiteSetting(SingletonModel):
    is_register_enabled = models.BooleanField(default=True)
    organizer_can_edit = ArrayField(models.CharField(max_length=30, choices=OrganizerEditableFields), default=list, blank=True)
    site_image = ProcessedImageField(upload_to="public/site", format="webP", null=True, blank=True) # type: ignore
    hero_image = ProcessedImageField(upload_to="public/hero", format="webP", null=True, blank=True) # type: ignore
    