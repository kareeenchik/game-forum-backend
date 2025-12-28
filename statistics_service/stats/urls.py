from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.get_all_logs, name='all_logs'),
    path('create/', views.create_log, name='create_log'),
]