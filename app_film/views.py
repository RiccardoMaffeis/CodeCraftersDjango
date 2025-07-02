# app_film/views.py

import json
import os
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from .models import Film, Proiezione, Sala


def film_schedule(request):
    # 1) Leggi parametri GET per date in formato “YYYY-MM-DD”
    start_date_str = request.GET.get("start-date", "")
    end_date_str = request.GET.get("end-date", "")
    today = datetime.now().date()

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        else:
            start_date = today - timedelta(days=today.weekday())
    except ValueError:
        start_date = today - timedelta(days=today.weekday())

    try:
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        else:
            end_date = start_date + timedelta(days=6)
    except ValueError:
        end_date = start_date + timedelta(days=6)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # 2) Costruisci lista di date “DD/MM/YYYY”, saltando martedì e mercoledì
    date_list = []
    current = start_date
    while current <= end_date:
        if current.weekday() not in (1, 2):
            date_list.append(current.strftime("%d/%m/%Y"))
        current += timedelta(days=1)

    # 3) Carica JSON locandine da static/utils/film_images.json
    json_path = os.path.join(settings.BASE_DIR, "static", "utils", "film_images.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            img_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        img_data = {}

    # 4) Per ogni data, recupera i film con proiezioni in quel giorno
    date_films = []
    for date_str in date_list:
        proiez_qs = Proiezione.objects.filter(data=date_str).select_related(
            "filmproiettato"
        )
        films_dict = {}
        for p in proiez_qs:
            f = p.filmproiettato
            if f.codice not in films_dict:
                img_url = img_data.get(str(f.codice), "")
                films_dict[f.codice] = {
                    "titolo": f.titolo,
                    "codice": f.codice,
                    "imgUrl": img_url,
                }
        date_films.append({"date": date_str, "films": list(films_dict.values())})

    context = {"date_films": date_films}
    return render(request, "app_film/film_schedule.html", context)


def lista_film(request):
    # 1) Leggi i parametri GET “start-date” e “end-date” e falli swap se invertiti
    start_str = request.GET.get("start-date")
    end_str = request.GET.get("end-date")
    date_format = "%Y-%m-%d"  # i <input type="date"> restituiscono YYYY-MM-DD

    if start_str and end_str:
        try:
            start_date = datetime.strptime(start_str, date_format).date()
            end_date = datetime.strptime(end_str, date_format).date()
        except ValueError:
            # formato non valido: ricadi sul default
            start_date = end_date = None

        if start_date and end_date:
            if start_date > end_date:
                start_date, end_date = end_date, start_date
    else:
        start_date = end_date = None

    # 2) Se non ho date valide, prendo da lunedì a domenica di questa settimana
    today = datetime.now().date()
    if not start_date or not end_date:
        monday = today - timedelta(days=today.weekday())
        start_date = monday
        end_date = monday + timedelta(days=6)

    # 3) Costruisco l'elenco delle date nel formato dd/mm/YYYY, saltando martedì(1) e mercoledì(2)
    dates = []
    ts = start_date
    while ts <= end_date:
        # Python weekday(): Lun=0, Mar=1, Mer=2...
        if ts.weekday() not in (1, 2):
            dates.append(ts.strftime("%d/%m/%Y"))
        ts += timedelta(days=1)

    # 4) Carico la mappa JSON delle locandine
    json_path = os.path.join(settings.BASE_DIR, "static", "utils", "film_images.json")
    try:
        with open(json_path, encoding="utf-8") as f:
            img_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        img_data = {}

    # 5) Per ogni giorno, prendo tutte le proiezioni e deduplichi per film
    date_films = []
    for date_str in dates:
        # Se il tuo campo Proiezione.data è DateField, converti la stringa:
        # data_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
        # qs = Proiezione.objects.filter(data=data_obj)
        # Se invece è testuale, filtra su data=date_str
        qs = (
            Proiezione.objects.filter(data=date_str)
            .select_related("filmproiettato", "sala")
            .order_by("ora")
        )

        films_dict = {}
        for p in qs:
            f = p.filmproiettato
            codice = str(f.codice)
            if codice not in films_dict:
                films_dict[codice] = {
                    "codice": codice,
                    "titolo": f.titolo,
                    "durata": f.durata,
                    "lingua": f.lingua,
                    "imgUrl": img_data.get(codice, ""),
                    "sala_numPosti": p.sala.numposti if p.sala else None,
                }
        date_films.append({"date": date_str, "films": list(films_dict.values())})

    return render(
        request,
        "app_film/film.html",
        {
            "date_films": date_films,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        },
    )


def movie_details(request):
    film_id = request.GET.get("film")
    date_str = request.GET.get("date")

    if not film_id or not date_str:
        return HttpResponseBadRequest("Parametri mancanti: 'film' e/o 'date'")

    # Carica JSON locandine da static/utils/film_images.json
    json_path = os.path.join(settings.BASE_DIR, "static", "utils", "film_images.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            img_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        img_data = {}

    image_url = img_data.get(str(film_id), "")

    film = get_object_or_404(Film, pk=film_id)

    proiezioni_qs = (
        Proiezione.objects.filter(filmproiettato_id=film_id, data=date_str)
        .select_related("sala")
        .order_by("ora")[:10]
    )

    icon_map = {
        "3-D": "https://cdn-icons-png.flaticon.com/128/83/83596.png",
        "tradizionale": "https://cdn-icons-png.flaticon.com/128/83/83467.png",
    }

    showtimes = []
    for p in proiezioni_qs:
        sala = p.sala
        icon_url = icon_map.get(sala.tipo) if (sala and sala.tipo) else ""
        showtimes.append(
            {
                "ora": p.ora[:5],
                "sala_numero": sala.numero if sala else None,
                "sala_tipo": sala.tipo if sala else None,
                "sala_dim": sala.dim if sala else None,
                "sala_numposti": sala.numposti if sala else None,
                "sala_numfile": sala.numfile if sala else None,
                "sala_numpostiperfila": sala.numpostiperfila if sala else None,
                "icon_url": icon_url,
            }
        )

    context = {
        "image_url": image_url,
        "film": {
            "codice": film.codice,
            "titolo": film.titolo,
            "anno": film.anno,
            "durata": film.durata,
            "lingua": film.lingua,
        },
        "filmDate": date_str,
        "showtimes": showtimes,
    }
    return render(request, "app_film/movie_details.html", context)


def search_film(request):
    term = request.GET.get("term", "").strip()
    # 1) Filtra i film
    if term:
        qs = Film.objects.filter(titolo__icontains=term)
    else:
        qs = Film.objects.all()

    # 2) Carica JSON delle immagini
    img_path = os.path.join(settings.BASE_DIR, "static", "utils", "film_images.json")
    try:
        with open(img_path, "r", encoding="utf-8") as f:
            images = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        images = {}

    # 3) Costruisci la lista di risultati
    results = []
    for film in qs:
        fid = str(film.codice)
        results.append(
            {
                "id": film.codice,
                "titolo": film.titolo,
                # se non c'è, metti un placeholder qualsiasi
                "immagine": images.get(fid, "https://example.com/images/default.jpg"),
            }
        )

    return JsonResponse(results, safe=False)
