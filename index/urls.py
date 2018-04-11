from django.urls import path

from . import views

app_name = 'index'
urlpatterns = [
    path('', views.index, name='index'),
    path('chooseuni/', views.chooseuni, name='chooseuni'),
    path('chooseuni/<slug:unicode>/', views.chooseuni, name='chooseuni'),
    path('clearcache/', views.clearcache, name='clearcache'),
]