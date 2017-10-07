from channels.routing import route
from . import consumers

channel_routing = [
    route('websocket.connect', consumers.waiting, path=r'^waiting/(?P<page>[\w|\W]+)/$'),
]
