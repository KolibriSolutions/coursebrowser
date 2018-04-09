from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('studyguide/', include('studyguide.urls')),
    path('admin/', admin.site.urls),
    path('', include('index.urls'))
]
