from django.urls import path

from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

from apps.pokerboard.consumers import TestConsumer

from .token_auth import TokenAuthMiddleware

ws_patterns = [
    path("ws/test/session/<int:id>", TestConsumer.as_asgi())
]

application = ProtocolTypeRouter({
  "http": AsgiHandler(),
  "websocket": 
    TokenAuthMiddleware(
        URLRouter(ws_patterns)
    )
})
