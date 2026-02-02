from django.db.models import signals
from django.dispatch import receiver
from .models import SiteSetting
import os

# @receiver([signals.pre_save, signals.post_delete], sender=SiteSetting)
# def check_image(sender, instance: SiteSetting, **kwargs):
#     print(kwargs)
#     if instance.site_image and os.path.exists(instance.site_image.path):
#         print(f"removing {instance.site_image.path}")
#         os.remove(instance.site_image.path)
