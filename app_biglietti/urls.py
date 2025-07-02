from django.urls import path
from . import views

app_name = 'app_biglietti'

urlpatterns = [
    path('prenota/', views.prenota_biglietto, name='prenota_biglietto'),
]
