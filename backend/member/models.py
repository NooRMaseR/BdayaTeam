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
    bdaya_user = models.OneToOneField(BdayaUser, on_delete=models.CASCADE, related_name="member")
    code = models.CharField(max_length=10, primary_key=True, unique=True, blank=True, validators=[validators.validate_member_code])
    collage_code = models.CharField(max_length=9, unique=True, validators=[validators.validate_collage_code])
    bonus = models.SmallIntegerField(default=0)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=MemberStatus, default=MemberStatus.NORMAL)

    @property
    def email(self) -> str:
        return self.bdaya_user.email

    @property
    def name(self) -> str:
        return self.bdaya_user.username
    
    @property
    def phone_number(self) -> str:
        return self.bdaya_user.phone_number

    class Meta:
        ordering = ("-track", "-joined_at")
        indexes = [
            models.Index(fields=["track", "joined_at"]),
        ]
        
    def __str__(self) -> str:
        return f'{self.name} - {self.code}'


def task_upload_path(instance: ReciviedTaskFile, filename: str) -> str:
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
