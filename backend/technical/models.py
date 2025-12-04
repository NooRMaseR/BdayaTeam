from django.db import models
from core.models import Track
from django.utils import timezone

# Create your models here.

class Task(models.Model):
    task_number = models.PositiveSmallIntegerField()
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    description = models.TextField()
    
    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at        
    
    class Meta:
        ordering = ['-task_number', '-created_at']
        unique_together = ("task_number", "track")

    def __str__(self):
        return f'Task #{self.task_number} for track {self.track}'
    