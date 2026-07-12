from django.dispatch import receiver
from django.db.models import signals
from core.models import BdayaUser
from contextlib import suppress
from pathlib import Path
from . import models

@receiver(signals.post_delete, sender=models.ReciviedTaskFile)
def delete_tasks_files(sender, instance: models.ReciviedTaskFile, **kwargs):
    with suppress(FileNotFoundError):
        Path(instance.file.path).unlink()
        

@receiver(signals.post_delete, sender=models.Member)
def delete_member_acc(sender, instance: models.Member, **kwargs):
    BdayaUser.objects.filter(email=instance.email).delete()
        
        