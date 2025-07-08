from django.urls import path
from . import views

app_name = 'app_biglietti'

urlpatterns = [
    path('prenota/', views.prenota_biglietto, name='prenota_biglietto'),
    path('get_proiezione_id/', views.get_proiezione_id, name='get_proiezione_id'),
    path('salva_parametri/', views.salva_parametri, name='salva_parametri'),
    path('get_sala_data/', views.get_sala_data, name='get_sala_data'),
    path('get_posti_occupati/', views.get_posti_occupati, name='get_posti_occupati'),
    path('salva_biglietti/', views.salva_biglietti, name='salva_biglietti'),
    path('send_ticket_email/', views.send_ticket_email, name='send_ticket_email'),
    path('clear_session/', views.clear_session, name='clear_session'),
]
