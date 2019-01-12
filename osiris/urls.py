from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'osiris'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/unicodes/', views.unicodes, name='unicodes'),
    path('api/<slug:uni>/<int:year>/course/<slug:code>/header/', views.getCourseHeader, name='getcourseheader'),
    # path('api/<slug:uni>/<int:year>/course/<slug:code>/info/', views.getCourseInfo, name='getcourseinfo'),
    path('api/<slug:uni>/faculties/', views.getFaculties, name='faculties'),
    path('api/<slug:uni>/types/', views.getTypes, name='types'),
    path('api/<slug:uni>/studies/', views.getStudies, name='studies'),
    # path('api/<slug:uni>/faculty/courses/<slug:faculty>/<slug:type>/', views.getCoursesFromFaculty, name='getcoursesfromfaculty'),
    url(r'^api/(?P<uni>[\w|\W]+)/(?P<year>[\d]+)/faculty/courses/(?P<faculty>[\w|\W]+)/(?P<type>[\w|\W]+)/$', views.getCoursesFromFaculty, name='getcoursesfromfaculty'),
]