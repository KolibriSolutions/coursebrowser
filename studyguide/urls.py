from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'studyguide'
urlpatterns = [
    url(r'^faculty/$', views.chooseFaculty, name='choosefaculty'),
    # path('courses/<slug:faculty>/<slug:type>/', views.listCourses, name='listcourses'),
    url(r'^courses/(?P<faculty>[\w|\W]+)/(?P<type>[\w|\W]+)/$', views.listCourses, name='listcourses'),
    # url(r'^courses/(?P<faculty>[\w|\W]+)/GS/$', views.listGS, name='listGS'),
    # url(r'^coursetree/(?P<faculty>[\w|\W]+)/(?P<type>\w+)/$', views.coursetree, name='coursetree'),
]