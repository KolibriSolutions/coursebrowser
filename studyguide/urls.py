from django.urls import path, re_path

from . import views

app_name = 'studyguide'
urlpatterns = [
    path('department/', views.choose_department, name=
    'choose_department'),
    re_path(r'^courses/(?P<department>[\w|\W]+)/(?P<type_shortname>[\w|\W]+)/(?P<year>[\d]+)/$', views.list_courses, name='list_courses'),
]
