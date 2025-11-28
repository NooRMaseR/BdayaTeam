from rest_framework.authtoken.models import Token
from member import models as member_models
from django.db.models import signals
from django.dispatch import receiver
from . import models as core_models


@receiver(signals.post_save, sender=core_models.BdayaUser)
def create_user_role(sender, instance: core_models.BdayaUser, created: bool, **kwargs):
    if created:
        Token.objects.create(user=instance)
        
    match instance.role:
        case core_models.UserRole.MEMBER:
            member_models.Member.objects.create()
            