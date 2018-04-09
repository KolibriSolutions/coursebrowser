# from channels.routing import route
# from . import consumers
#
# channel_routing = [
#     route('websocket.connect', consumers.waiting, path=r'^waiting/(?P<page>[\w|\W]+)/$'),
# ]

from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^waiting/(?P<page>[\w|\W]+)/$', consumers.WaitingConsumer),
]