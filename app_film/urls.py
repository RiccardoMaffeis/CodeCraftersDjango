from django.urls import path
from . import views

app_name = 'app_film'

urlpatterns = [
    path('film/', views.lista_film, name='lista_film'),
    path('movie_details/', views.movie_details, name='movie_details'),
    path('search_film/', views.search_film, name='search_film'),
    path('film_schedule/', views.film_schedule, name='film_schedule'),
    path('get_options_by_film/', views.get_options_by_film, name='get_options_by_film'),
    path('get_options_by_film_and_date/', views.get_options_by_film_and_date, name='get_options_by_film_and_date'),
    path('get_options_by_film_and_date_and_time/', views.get_options_by_film_and_date_and_time, name='get_options_by_film_and_date_and_time'),
]
