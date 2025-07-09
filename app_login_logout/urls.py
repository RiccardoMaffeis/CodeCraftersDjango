# app_login_logout/urls.py

from django.urls import path
from . import views

app_name = "app_login_logout"

urlpatterns = [
    path("", views.auth_view, name="auth"),
    path("login/", views.login_view, name="login"),
    path("login_json/", views.api_login, name="login_json"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path('auth_login/', views.auth_login, name='auth_login'),
    path('auth_register/', views.auth_register, name='auth_register'),
]
