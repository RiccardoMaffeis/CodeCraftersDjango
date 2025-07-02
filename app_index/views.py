# app_index/views.py

import json
import os
from datetime import datetime, timedelta
from django.shortcuts import render
from django.conf import settings
from app_film.models import Film, Proiezione, Sala

def index_view(request):
    # 1) Calcolo delle date della settimana
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week   = start_of_week + timedelta(days=6)

    dates = []
    current = start_of_week
    while current <= end_of_week:
        if current.weekday() not in (1, 2):  # salta martedì e mercoledì
            dates.append(current.strftime('%d/%m/%Y'))
        current += timedelta(days=1)

    # 2) Carica JSON delle immagini
    json_path = os.path.join(settings.BASE_DIR, 'static', 'utils', 'film_images.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            img_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        img_data = {}

    # 3) Per ogni data, recupera (via stringa) la prima proiezione
    date_films = []
    for date_str in dates:
        # NON converto più in date, uso direttamente la stringa "dd/mm/YYYY"
        proiez_qs = (
            Proiezione.objects
            .filter(data=date_str)  # filtro direttamente su "dd/mm/YYYY"
            .select_related('filmproiettato', 'sala')
            .order_by('ora')[:1]
        )

        films_dict = {}
        for p in proiez_qs:
            f = p.filmproiettato
            # Recupera l’immagine dal JSON (o default se non esiste)
            img_url = img_data.get(str(f.codice), '/static/immagini/default.jpg')

            # La relazione `p.sala` è un ForeignKey a Sala, quindi p.sala.numPosti funziona
            try:
                num_posti = p.sala.numposti
            except Sala.DoesNotExist:
                num_posti = None

            if f.codice not in films_dict:
                films_dict[f.codice] = {
                    'codice': f.codice,
                    'titolo': f.titolo,
                    'durata': f.durata,
                    'lingua': f.lingua,
                    'imgUrl': img_url,
                    'sala_numPosti': num_posti,
                }

        date_films.append({'date': date_str, 'films': list(films_dict.values())})

    # 4) Render del template
    context = {'date_films': date_films}
    return render(request, 'app_index/index.html', context)
