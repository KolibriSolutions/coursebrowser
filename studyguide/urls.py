from django.conf.urls import url

from . import views

app_name = 'studyguide'
urlpatterns = [
    url(r'^faculty/$', views.chooseFaculty, name='choosefaculty'),
    url(r'^courses/(?P<faculty>[\w|\W]+)/BC/$', views.listBC, name='listBC'),
    url(r'^courses/(?P<faculty>[\w|\W]+)/GS/$', views.listGS, name='listGS'),
]