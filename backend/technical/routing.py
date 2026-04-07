from django.urls import path
from .consumers import LiveMemberEditConsumer, OnlineTechnicalTaskConsumer

websocket_urlpatterns =  [
    path("ws/technical/edit-member/<str:track_name>/", LiveMemberEditConsumer.as_asgi()), # type: ignore
    path("ws/technical/live-online-tasks/<str:track_name>/", OnlineTechnicalTaskConsumer.as_asgi()), # type: ignore
]