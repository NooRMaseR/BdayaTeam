from enum import StrEnum
from django.db import models
from core.models import Track
from django.utils import timezone
from imagekit.models import ProcessedImageField
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class MemberTechEditType(StrEnum):
    NOTES = "notes"
    DEGREE = "degree"
    
def task_images_url(instance, filename: str) -> str:
    return f"public/{instance.task.track.name}/task/{instance.task.task_number}/{filename}"

class Task(models.Model):
    task_number = models.PositiveSmallIntegerField()
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    description = models.TextField()
    links = ArrayField(models.URLField(), null=True, blank=True)
    
    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
    
    class Meta:
        ordering = ('task_number', '-track_id')
        unique_together = ("task_number", "track")

    def __str__(self) -> str:
        return f'Task #{self.task_number} for track {self.track}'
    
class TaskImage(models.Model):
    task = models.ForeignKey(Task, models.CASCADE, related_name="images")
    image = ProcessedImageField(upload_to=task_images_url, format="webP", null=True, blank=True) # type: ignore
    