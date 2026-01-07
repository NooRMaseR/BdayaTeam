from django.dispatch import receiver
from django.db.models import signals
from core.models import BdayaUser
from . import models
import os


@receiver(signals.post_delete, sender=models.ReciviedTaskFile)
def delete_tasks_files(sender, instance: models.ReciviedTaskFile, **kwargs):
    file = instance.file.path
    if os.path.exists(file):
        os.remove(file)
        

@receiver(signals.post_delete, sender=models.Member)
def delete_member_acc(sender, instance: models.Member, **kwargs):
    BdayaUser.objects.filter(email=instance.email).delete()
        
        