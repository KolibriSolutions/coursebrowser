from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'studyguide'
urlpatterns = [
    url(r'^faculty/$', views.chooseFaculty, name='choosefaculty'),
    url(r'^courses/(?P<faculty>[\w|\W]+)/(?P<type>[\w|\W]+)/(?P<year>[\d]+)/$', views.listCourses, name='listcourses'),
]