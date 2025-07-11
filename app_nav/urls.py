from django.urls import path
from . import views

app_name = 'app_nav'

urlpatterns = [
    path('', views.database_view, name='dashboard'),
    path('subscribe_newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
]
