from django.db import models
from member.models import Member
from django.core.exceptions import ValidationError

# Create your models here.

class AttendanceStatus(models.TextChoices):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"

class Attendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=9, choices=AttendanceStatus)
    excuse_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ("member", "date")
        
    def clean(self) -> None:
        if self.status == AttendanceStatus.EXCUSED and not self.excuse_reason:
            raise ValidationError("an excuse reasoon must be set")
        return super().clean()
    
    def __str__(self):
        return f"{self.member} - {self.date}"
    

    

