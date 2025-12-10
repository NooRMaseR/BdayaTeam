from phonenumber_field.modelfields import PhoneNumberField
from technical.models import Task
from core.models import Track
from django.db import models
from core import validators

# Create your models here.

class Member(models.Model):
    code = models.CharField(max_length=6, primary_key=True, db_index=True, unique=True, blank=True, validators=[validators.validate_member_code])
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    collage_code = models.CharField(max_length=9, unique=True, validators=[validators.validate_collage_code])
    phone_number = PhoneNumberField(region="EG") # type: ignore
    bonus = models.SmallIntegerField(default=0)
    track = models.ForeignKey(Track, on_delete=models.PROTECT, related_name='members')

    def __str__(self):
        return f'{self.name} - {self.code}'


def task_upload_path(instance: ReciviedTaskFile, filename: str):
    return f"tasks/{instance.recivied_task.member.name}/{instance.recivied_task.task.task_number}/{filename}"

class ReciviedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="recivied")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="tasks_sent")
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)
    degree = models.PositiveSmallIntegerField(null=True, blank=True)
    signed = models.BooleanField(default=False)
    recived_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs) -> None:
        if self.signed == False and self.degree is not None:
            self.signed = True
        return super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ("task", "member")
    
    def __str__(self) -> str:
        return f"Recived Task {self.task.task_number} from {self.member}"
    
class ReciviedTaskFile(models.Model):
    recivied_task = models.ForeignKey(ReciviedTask, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=task_upload_path, blank=True, null=True)
    
    