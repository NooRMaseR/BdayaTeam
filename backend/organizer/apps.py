from django.apps import AppConfig


class OrganizerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'organizer'
    
    def ready(self) -> None:
        from . import signals
        return super().ready()
