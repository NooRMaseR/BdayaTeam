from rest_framework.authtoken.models import Token
from member import models as member_models
from django.db.models import signals
from django.dispatch import receiver
from .tasks import send_member_email
from . import models as core_models

@receiver(signals.post_save, sender=core_models.BdayaUser)
def create_user_token(sender, instance: core_models.BdayaUser, created: bool, **kwargs):
    if created:
        Token.objects.create(user=instance)


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
        send_member_email.delay( # type: ignore
            instance.name,
            instance.email,
            GENERATED_PASSWORD,
            instance.code,
            instance.track.track
        )
        