from django.db import models
from core.models import BdayaUser, Track

# Create your models here.

class Technical(models.Model):
    user = models.OneToOneField(BdayaUser, on_delete=models.CASCADE, related_name='technical_profile')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='technicals')

    def __str__(self):
        return f'{self.user.username} — {self.track}'

class Task(models.Model):
    task_number = models.PositiveIntegerField()
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="tasks")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    # degree = models.PositiveSmallIntegerField(blank=True, null=True)
    # signed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-task_number', '-uploaded_at']
        unique_together = ("task_number", "track")

    def __str__(self):
        return f'Task #{self.task_number}'
    
    # def save(self, *args, **kwargs) -> None:
    #     if self.degree is not None and self.signed == False:
    #         self.signed = True
    #     return super().save(*args, **kwargs)