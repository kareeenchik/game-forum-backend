from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Исправлено: заменяем 'api.urls' на 'stats.urls'
    path('api/v1/logs/', include('stats.urls')), 
]