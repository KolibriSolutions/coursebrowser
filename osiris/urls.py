from django.urls import path, re_path, include

from . import views

app_name = 'osiris'
url_patterns_v2 = [
    path('courses/all/', views.get_all_courses, name='getallcourses'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('api/unicodes/', views.unicodes, name='unicodes'),
    path('api/<slug:uni>/<int:year>/course/<slug:code>/header/', views.get_course_header, name='getcourseheader'),
    # path('api/<slug:uni>/<int:year>/course/<slug:code>/info/', views.getCourseInfo, name='getcourseinfo'),
    path('api/<slug:uni>/faculties/', views.get_departments, name='faculties'),
    path('api/<slug:uni>/types/', views.get_type_names, name='types'),
    path('api/<slug:uni>/studies/', views.get_studies, name='studies'),
    # path('api/<slug:uni>/faculty/courses/<slug:faculty>/<slug:type>/', views.getCoursesFromFaculty, name='getcoursesfromfaculty'),
    re_path(r'^api/(?P<uni>[\w|\W]+)/(?P<year>[\d]+)/faculty/courses/(?P<department>[\w|\W]+)/(?P<type_shortname>[\w|\W]+)/$',
            views.get_courses_from_faculty, name='getcoursesfromfaculty'),
    path('api/v2/<slug:uni>/<int:year>/', include(url_patterns_v2)),
]
