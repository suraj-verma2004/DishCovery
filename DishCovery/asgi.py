import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing 

os.environ.setdefault('django.settings.module', 'DishCovery.settings')

# ASGI gateway
application = ProtocolTypeRouter({
    
    "http": get_asgi_application(),

   #websocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})