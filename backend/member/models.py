from phonenumber_field.modelfields import PhoneNumberField
from django.shortcuts import get_object_or_404
from core.models import BdayaUser, Track
from technical.models import Task
from django.db import models
from core import validators

# Create your models here.

class MemberStatus(models.TextChoices):
    NORMAL = "normal"
    WARNING1 = "warning 1"
    WARNING2 = "warning 2"
    FIRED = "fired"

class Member(models.Model):
    code = models.CharField(max_length=10, primary_key=True, unique=True, blank=True, validators=[validators.validate_member_code])
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    collage_code = models.CharField(max_length=9, unique=True, validators=[validators.validate_collage_code])
    phone_number = PhoneNumberField(region="EG", unique=True) # type: ignore
    bonus = models.SmallIntegerField(default=0)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=MemberStatus, default=MemberStatus.NORMAL)

    @property
    def bdaya_user(self) -> BdayaUser:
        return get_object_or_404(BdayaUser.objects.only('id', 'email'), email=self.email)
    
    class Meta:
        ordering = ("-track", "-joined_at")
        indexes = [
            models.Index(fields=["track", "joined_at"]),
        ]
        
    def __str__(self):
        return f'{self.name} - {self.code}'


def task_upload_path(instance: ReciviedTaskFile, filename: str):
    return f"protected/tasks/{instance.recivied_task.member.code}/{instance.recivied_task.task.task_number}/{filename}"

class ReciviedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="recivied")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="tasks_sent")
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)
    technical_notes = models.TextField(null=True, blank=True)
    degree = models.PositiveSmallIntegerField(null=True, blank=True)
    signed = models.BooleanField(default=False)
    recived_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("task", "member")
    
    def __str__(self) -> str:
        return f"Recived Task {self.task.task_number} from {self.member}"
    
class ReciviedTaskFile(models.Model):
    recivied_task = models.ForeignKey(ReciviedTask, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=task_upload_path, blank=True, null=True)
