# app_utente/urls.py

from django.urls import path
from . import views

app_name = 'app_utente'

urlpatterns = [
    path('profile/', views.profile, name='profile'),  
    path(
        'elimina/<int:num_proiezione>/<int:num_fila>/<int:num_posto>/',
        views.elimina_biglietto,
        name='elimina_biglietto'
    ),
]
