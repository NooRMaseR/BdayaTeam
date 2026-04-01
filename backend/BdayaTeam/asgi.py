"""
ASGI config for BdayaTeam project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BdayaTeam.settings')
app = get_asgi_application()

import technical.routing as tech_websocket_routing
import organizer.routing as org_websocket_routing
import core.routing as core_websocket_routing
from core.middleware import JWTSocketMiddleware

application = ProtocolTypeRouter({
    "http": app,
    "websocket": JWTSocketMiddleware(
        URLRouter(
            org_websocket_routing.websocket_urlpatterns
            + tech_websocket_routing.websocket_urlpatterns
            + core_websocket_routing.websocket_urlpatterns
        )
    )
})
