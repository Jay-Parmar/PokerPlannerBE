import os
import django

from django.urls import path
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

from apps.pokerboard.consumers import SessionConsumer

from .token_auth import TokenAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PokerPlanner.settings')
django.setup()

ws_patterns = [
    path("ws/session/<int:id>", SessionConsumer.as_asgi())
]

application = ProtocolTypeRouter({
  "http": AsgiHandler(),
  "websocket": 
    TokenAuthMiddleware(
        URLRouter(ws_patterns)
    )
})
