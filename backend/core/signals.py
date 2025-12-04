from django.template.loader import render_to_string
from member import models as member_models
from django.core.mail import send_mail
from django.db.models import signals
from django.dispatch import receiver
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
        )
        user.set_password(GENERATED_PASSWORD)
        user.save()
        
        template = render_to_string(
            "register_email.html", 
            {
                "username": instance.name,
                "email": instance.email,
                "password": GENERATED_PASSWORD,
                "code": instance.code,
                "track": instance.track.track
            }
        )
        send_mail(
            "Team Bdaya Info",
            "Welcome",
            from_email=None,
            recipient_list=[instance.email],
            html_message=template
        )
        

            