# app_biglietti/views.py

import json
import os
from django.shortcuts import render, redirect
from django.conf import settings
from app_film.models import Film, Proiezione

def prenota_biglietto(request):
    # 1) Recupera film_id, date_param, time_param e sala_param da GET o da sessione
    if 'film' in request.GET:
        film_id = int(request.GET.get('film'))
        # Se cambia il film, resetta orario, sala e stato prenotazione
        if request.session.get('film') != film_id:
            request.session.pop('orario', None)
            request.session.pop('sala', None)
            request.session.pop('booking_state', None)
        request.session['film'] = film_id
    else:
        film_id = request.session.get('film', 0)

    if 'date' in request.GET:
        date_param = request.GET.get('date')
        request.session['date'] = date_param
    else:
        date_param = request.session.get('date', '')

    if 'orario' in request.GET:
        time_param = request.GET.get('orario')[:5]
        request.session['orario'] = time_param
    else:
        time_param = request.session.get('orario', '')

    if 'sala' in request.GET:
        sala_param = request.GET.get('sala')
        request.session['sala'] = sala_param
    else:
        sala_param = request.session.get('sala', '')

    # Se tutti i parametri sono stati passati via GET, redirige alla stessa vista
    if ( ('film' not in request.GET or 'date' not in request.GET or
          'orario' not in request.GET or 'sala' not in request.GET ) 
         and film_id and date_param and time_param and sala_param ):
        query = f"?film={film_id}&date={date_param}&orario={time_param}&sala={sala_param}"
        return redirect(request.path + query)

    # 2) Carica i dati del film
    titolo = ''
    durata = ''
    lingua = ''
    poster_url = 'default.jpg'
    if film_id:
        try:
            film = Film.objects.get(codice=film_id)
            titolo = film.titolo
            durata = film.durata
            lingua = film.lingua
        except Film.DoesNotExist:
            film = None

        # Legge film_images.json da static/immagini/film_images.json
        json_path = os.path.join(settings.BASE_DIR, 'static', 'immagini', 'film_images.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                images = json.load(f)
            poster_url = images.get(str(film_id), 'default.jpg')
        except (FileNotFoundError, json.JSONDecodeError):
            poster_url = 'default.jpg'

    # 3) Recupera gli orari disponibili per quel film e quella data
    times = []
    if film_id and date_param:
        qs_times = Proiezione.objects.filter(
            filmProiettato_id=film_id,
            data=date_param
        ).order_by('ora').values_list('ora', flat=True)
        # usa le stringhe "HH:MM:SS"; nel template si fa slice[0:5]
        times = [t.strftime('%H:%M:%S') for t in qs_times]

    # 4) Prepara il context e renderizza il template
    context = {
        'film_id': film_id,
        'date_param': date_param,
        'time_param': time_param,
        'sala_param': sala_param,
        'film_data': {
            'titolo': titolo,
            'durata': durata,
            'lingua': lingua,
        },
        'poster_url': poster_url,
        'times': times,
        'user_mail': request.user.email if request.user.is_authenticated else None,
    }
    return render(request, 'app_biglietti/biglietti.html', context)
