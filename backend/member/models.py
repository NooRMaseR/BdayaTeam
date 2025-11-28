from typing import Iterable
from phonenumber_field.modelfields import PhoneNumberField
from technical.models import Task
from core.models import Track
from django.db import models
from core import validators

# Create your models here.

class Member(models.Model):
    name = models.CharField(max_length=200, unique=True)
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=6, unique=True, blank=True, validators=[validators.validate_student_code])
    collage_code = models.CharField(max_length=50, unique=True, validators=[validators.validate_collage_code])
    phone_number = PhoneNumberField(region="EG") # type: ignore
    track = models.ForeignKey(Track, on_delete=models.PROTECT, related_name='members')

    def __str__(self):
        return f'{self.name} ({self.code})'


class ReciviedTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    file = models.FileField(upload_to=f'tasks/{member.name} {task} %Y/%m/%d/', blank=True, null=True)
    notes = models.TextField(null=True, blank=True)
    degree = models.PositiveSmallIntegerField(null=True, blank=True)
    signed = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs) -> None:
        if self.signed == False and self.degree is not None:
            self.signed = True
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"Recived Task {self.task.task_number} from {self.member}"