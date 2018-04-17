from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import index.routing
import osiris.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(index.routing.websocket_urlpatterns +
                osiris.routing.websocket_urlpatterns
        )
    ),
})