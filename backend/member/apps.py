from django.apps import AppConfig


class MemberConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'member'
    
    def ready(self) -> None:
        from . import signals
        return super().ready()
