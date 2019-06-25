from django.urls import path, re_path

from . import views

app_name = 'osiris'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/unicodes/', views.unicodes, name='unicodes'),
    path('api/<slug:uni>/<int:year>/course/<slug:code>/header/', views.getCourseHeader, name='getcourseheader'),
    # path('api/<slug:uni>/<int:year>/course/<slug:code>/info/', views.getCourseInfo, name='getcourseinfo'),
    path('api/<slug:uni>/faculties/', views.get_departments, name='faculties'),
    path('api/<slug:uni>/types/', views.get_type_names, name='types'),
    path('api/<slug:uni>/studies/', views.getStudies, name='studies'),
    # path('api/<slug:uni>/faculty/courses/<slug:faculty>/<slug:type>/', views.getCoursesFromFaculty, name='getcoursesfromfaculty'),
    re_path(r'^api/(?P<uni>[\w|\W]+)/(?P<year>[\d]+)/faculty/courses/(?P<faculty>[\w|\W]+)/(?P<type>[\w|\W]+)/$', views.getCoursesFromFaculty, name='getcoursesfromfaculty'),
]
