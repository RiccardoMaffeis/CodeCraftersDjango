# app_database/urls.py
from django.urls import path
from . import views

app_name = 'app_database'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
]
