from django.conf.urls import url
from .import consumers

websocket_urlpatterns = [
    url(r'^osiris/api/ws/(?P<unicode>[\w|\W]+)/course/$', consumers.ApiRespondCourse),
    url(r'^osiris/api/ws/(?P<unicode>[\w|\W]+)/faculty/$', consumers.ApiRespondFaculty),
]