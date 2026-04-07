from django.urls import path
from .consumers import LiveMemberEditConsumer

websocket_urlpatterns =  [
    path("ws/organizer/edit-member/<str:track_name>/", LiveMemberEditConsumer.as_asgi()), # type: ignore
]