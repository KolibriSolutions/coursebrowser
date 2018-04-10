from django.urls import path

from . import views

app_name = 'osiris'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/unicodes/', views.unicodes, name='unicodes'),
    path('api/<slug:uni>/course/<slug:code>/', views.getCourse, name='getcourse'),
    path('api/<slug:uni>/faculties/', views.getFaculties, name='faculties'),
    path('api/<slug:uni>/types/', views.getTypes, name='types'),
    path('api/<slug:uni>/faculty/courses/<slug:faculty>/<slug:type>/', views.getCoursesFromFaculty, name='getcoursesfromfaculty'),
]