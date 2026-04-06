from member import models as member_models
from django.db.models import signals
from django.dispatch import receiver
from . import models as core_models
        
@receiver(signals.post_delete, sender=core_models.BdayaUser)
@receiver(signals.post_delete, sender=member_models.Member)
def full_user_delete(sender, instance: core_models.BdayaUser | member_models.Member, **kwargs) -> None:
    core_models.BdayaUser.objects.filter(email=instance.email).delete()
