# app_film/views.py

import json
import os
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from .models import Film, Proiezione, Sala

def film_schedule(request):
    start_date_str = request.GET.get("start_date", "")
    end_date_str = request.GET.get("end_date", "")
    today = datetime.now().date()
    print("CHIAMATA film_schedule:", start_date_str, "->", end_date_str)
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else today - timedelta(days=today.weekday())
    except ValueError:
        start_date = today - timedelta(days=today.weekday())

    try:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else start_date + timedelta(days=6)
    except ValueError:
        end_date = start_date + timedelta(days=6)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    date_list = []
    current = start_date
    while current <= end_date:
        if current.weekday() not in (1, 2):
            date_list.append(current.strftime("%d/%m/%Y"))
        current += timedelta(days=1)

    json_path = os.path.join(settings.BASE_DIR, "static", "utils", "film_images.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            img_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        img_data = {}

    date_films = []
    for date_str in date_list:
        proiez_qs = Proiezione.objects.filter(data=date_str).select_related("filmproiettato")
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

    return JsonResponse({"date_films": date_films})

def lista_film(request):
    start_str = request.GET.get("start-date")
    end_str = request.GET.get("end-date")
    date_format = "%Y-%m-%d"

    if start_str and end_str:
        try:
            start_date = datetime.strptime(start_str, date_format).date()
            end_date = datetime.strptime(end_str, date_format).date()
        except ValueError:
            start_date = end_date = None

        if start_date and end_date:
            if start_date > end_date:
                start_date, end_date = end_date, start_date
    else:
        start_date = end_date = None

    today = datetime.now().date()
    if not start_date or not end_date:
        monday = today - timedelta(days=today.weekday())
        start_date = monday
        end_date = monday + timedelta(days=6)

    dates = []
    ts = start_date
    while ts <= end_date:
        if ts.weekday() not in (1, 2):
            dates.append(ts.strftime("%d/%m/%Y"))
        ts += timedelta(days=1)

    json_path = os.path.join(settings.BASE_DIR, "static", "utils", "film_images.json")
    try:
        with open(json_path, encoding="utf-8") as f:
            img_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        img_data = {}

    date_films = []
    for date_str in dates:
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
    if term:
        qs = Film.objects.filter(titolo__icontains=term)
    else:
        qs = Film.objects.all()

    img_path = os.path.join(settings.BASE_DIR, "static", "utils", "film_images.json")
    try:
        with open(img_path, "r", encoding="utf-8") as f:
            images = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        images = {}

    results = []
    for film in qs:
        fid = str(film.codice)
        results.append(
            {
                "id": film.codice,
                "titolo": film.titolo,
                "immagine": images.get(fid, "https://example.com/images/default.jpg"),
            }
        )

    return JsonResponse(results, safe=False)

def get_options_by_film(request):
    film_id = request.GET.get('film_id')
    if not film_id:
        return JsonResponse({'error': 'Missing film_id'}, status=400)

    sale_qs = Sala.objects.filter(proiezioni__filmproiettato=film_id).distinct().values('numero', 'tipo')

    date_qs = Proiezione.objects.filter(filmproiettato=film_id).values_list('data', flat=True).distinct()
    orari_qs = Proiezione.objects.filter(filmproiettato=film_id).values_list('ora', flat=True).distinct()

    date = [{'data': d} for d in date_qs]

    return JsonResponse({
        'sale': list(sale_qs),
        'date': date,
        'orari': list(orari_qs)
    })
    
def get_options_by_film_and_date(request):
    film_id = request.GET.get('film_id')
    data = request.GET.get('data')

    if not film_id or not data:
        return JsonResponse({'error': 'Parametri mancanti'}, status=400)

    try:
        sale_qs = Sala.objects.filter(
            proiezioni__filmproiettato__codice=film_id,
            proiezioni__data=data
        ).distinct().values('numero', 'tipo')

        orari_qs = Proiezione.objects.filter(
            filmproiettato__codice=film_id,
            data=data
        ).values('ora')

        return JsonResponse({
            'sale': list(sale_qs),
            'orari': list(orari_qs)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_options_by_film_and_date_and_time(request):
    film_id = request.GET.get("film_id")
    data = request.GET.get("data")
    ora = request.GET.get("ora")

    if not (film_id and data and ora):
        return JsonResponse({"error": "Parametri mancanti"}, status=400)

    proiezioni = Proiezione.objects.filter(
        filmproiettato_id=film_id,
        data=data,
        ora__startswith=ora
    ).select_related("sala")

    sale = []
    for p in proiezioni:
        sala = p.sala
        if sala:
            sale.append({
                "numero": sala.numero,
                "tipo": sala.tipo,
            })

    return JsonResponse({"sale": sale})