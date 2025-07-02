from django.urls import path
from . import views

app_name = 'app_film'

urlpatterns = [
    path('film/', views.lista_film, name='lista_film'),
    path('movie_details/', views.movie_details, name='movie_details'),
    path('search_film/', views.search_film, name='search_film'),
]
