from django.urls import path
from .consumers import NotificationConsumer

websocket_urlpatterns = [
    path("ws/technical/notify/<str:track_name>/", NotificationConsumer.as_asgi()), # type: ignore
]