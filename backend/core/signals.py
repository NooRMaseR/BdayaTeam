from member import models as member_models
from django.db.models import signals
from django.dispatch import receiver
from .tasks import send_member_email
from . import models as core_models


@receiver(signals.post_save, sender=member_models.Member)
def create_user_from_member(sender, instance: member_models.Member, created: bool, **kwargs):
    if created:
        GENERATED_PASSWORD = f"{instance.code}_{instance.collage_code}"
        
        user = core_models.BdayaUser(
            username=instance.name,
            phone_number=instance.phone_number,
            email=instance.email,
            role=core_models.UserRole.MEMBER,
            track=instance.track
        )
        user.set_password(GENERATED_PASSWORD)
        user.save()
        send_member_email(
            instance.name,
            instance.email,
            GENERATED_PASSWORD,
            instance.code,
            instance.track.track
        )
        
@receiver(signals.post_delete, sender=core_models.BdayaUser)
@receiver(signals.post_delete, sender=member_models.Member)
def full_user_delete(sender, instance: core_models.BdayaUser | member_models.Member, **kwargs):
    match type(instance):
        case core_models.BdayaUser:
            member_models.Member.objects.filter(email=instance.email).delete()
            
        case member_models.Member:
            core_models.BdayaUser.objects.filter(email=instance.email).delete()
