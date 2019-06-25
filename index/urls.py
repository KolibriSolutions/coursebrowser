from django.urls import path

from . import views

app_name = 'index'
urlpatterns = [
    path('', views.index, name='index'),
    path('choose_university/', views.choose_university, name='choose_university'),
    path('choose_university/<slug:university_code>/', views.choose_university, name='choose_university'),
    path('clearcache/', views.clearcache, name='clearcache'),
]
