from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    url(r'^waiting/(?P<page>[\w|\W]+)/$', consumers.WaitingConsumer),
]