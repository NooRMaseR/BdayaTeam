from django.db import models
from core.models import BdayaUser

# Create your models here.

class PushSubscription(models.Model):
    user = models.ForeignKey(BdayaUser, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.URLField(max_length=500)
    auth = models.CharField(max_length=100)
    p256dh = models.CharField(max_length=100)

    class Meta:
        unique_together = ("user", "endpoint")