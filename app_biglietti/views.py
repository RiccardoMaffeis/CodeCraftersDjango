# app_biglietti/views.py

from datetime import date
from django.core.mail import EmailMessage
import json
import os
from traceback import format_tb
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from app_biglietti.models import Biglietto
from app_film.models import Film, Proiezione, Sala
from django.views.decorators.csrf import csrf_exempt

def prenota_biglietto(request):
    if 'film' in request.GET:
        film_id = int(request.GET.get('film'))
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

    if ( ('film' not in request.GET or 'date' not in request.GET or
          'orario' not in request.GET or 'sala' not in request.GET ) 
         and film_id and date_param and time_param and sala_param ):
        query = f"?film={film_id}&date={date_param}&orario={time_param}&sala={sala_param}"
        return redirect(request.path + query)

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

        json_path = os.path.join(settings.BASE_DIR, 'static', 'utils', 'film_images.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                images = json.load(f)
            poster_url = images.get(str(film_id), 'default.jpg')
        except (FileNotFoundError, json.JSONDecodeError):
            poster_url = 'default.jpg'

    times = []
    if film_id and date_param:
        qs_times = Proiezione.objects.filter(
            filmproiettato_id=film_id,
            data=date_param
        ).order_by('ora').values_list('ora', flat=True)
        times = list(qs_times)

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

def get_proiezione_id(request):
    film = request.GET.get('film')
    data = request.GET.get('data')
    ora = request.GET.get('ora')

    # Normalizzazione orario in formato HH:MM:SS
    if ora:
        parts = ora.split(':')
        if len(parts) >= 2:
            hh = int(parts[0])
            mm = int(parts[1])
            ss = int(parts[2]) if len(parts) > 2 else 0
            ora = f"{hh:02d}:{mm:02d}:{ss:02d}"
        else:
            return JsonResponse({'proiezioneId': None, 'message': 'Orario non valido'}, status=400)

    if not all([film, data, ora]):
        return JsonResponse({'proiezioneId': None, 'message': 'Parametri mancanti'}, status=400)

    proiezione = Proiezione.objects.filter(
        filmproiettato=film,
        data=data,
        ora=ora
    ).values('numproiezione', 'sala').first()

    if proiezione:
        return JsonResponse({
            'proiezioneId': proiezione['numproiezione'],
            'sala': proiezione['sala']
        })
    else:
        return JsonResponse({
            'proiezioneId': None,
            'sala': None,
            'message': 'Proiezione non trovata'
        }, status=404)
     
def salva_parametri(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            request.session['sala'] = data.get('sala')
            orario = data.get('orario')
            request.session['orario'] = orario[:5] if orario else None
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Metodo non consentito'}, status=405)
    
def get_sala_data(request):
    sala_id = request.GET.get('id')

    if not sala_id or not sala_id.isdigit():
        return JsonResponse({'error': 'ID sala non valido'}, status=400)

    try:
        sala = Sala.objects.get(numero=int(sala_id))
        return JsonResponse({
            'numFile': sala.numfile,
            'numPostiPerFila': sala.numpostiperfila 
        })
    except Sala.DoesNotExist:
        return JsonResponse({'error': 'Sala non trovata'}, status=404)
    
def get_posti_occupati(request):
    proiezione_id = request.GET.get('proiezione')
    if not proiezione_id:
        return JsonResponse({'errore': 'ID mancante'}, status=400)

    biglietti = Biglietto.objects.filter(numproiezione=proiezione_id)
    posti = [
        f"{b.numfila.upper()}{b.numposto}"
        for b in biglietti
        if b.numfila and b.numposto is not None
    ]
    return JsonResponse(posti, safe=False)

def salva_biglietti(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Metodo non consentito'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON non valido'}, status=400)

    proiezione_id = data.get('proiezioneId')
    posti = data.get('posti')
    prezzi = data.get('prezzi')
    email = data.get('mail', '').strip()

    if not proiezione_id or not posti or not prezzi or len(posti) != len(prezzi):
        return JsonResponse({'status': 'error', 'message': 'Dati mancanti o non validi'}, status=400)

    try:
        for i, posto in enumerate(posti):
            fila = posto[0].upper()  # Prima lettera (A, B, C...)
            numero = int(posto[1:])  # Da posizione 1 in poi (numero)

            Biglietto.objects.create(
                numproiezione=proiezione_id,
                numfila=fila,
                numposto=numero,
                datavendita=date.today(),
                prezzo=str(prezzi[i]),
                email=email
            )

        return JsonResponse({
            'status': 'ok',
            'debug': {
                'proiezioneId': proiezione_id,
                'posti': posti,
                'prezzi': prezzi,
                'email': email
            }
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Errore DB',
            'error': str(e)
        }, status=500)
        
def send_ticket_email(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'method_not_allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'invalid_json'}, status=400)

    email = request.session.get('mail') or data.get('email')
    if not email or '@' not in email:
        return JsonResponse({'status': 'invalid_email'}, status=400)

    film = data.get('film')
    orario = data.get('orario')
    posti = data.get('posti')
    totale = data.get('totale')

    subject = "🎫 Conferma Prenotazione - CodeCrafter"
    html_message = f"""
        <html>
        <head><meta charset='UTF-8'><title>Conferma Prenotazione</title></head>
        <body>
            <h2 style='color:#580000;'>Conferma Prenotazione</h2>
            <p><strong>Film:</strong> {film}</p>
            <p><strong>Orario:</strong> {orario}</p>
            <p><strong>Posti:</strong> {posti}</p>
            <p><strong>Totale:</strong> €{totale}</p>
            <p style='margin-top:20px;'>Grazie per aver prenotato con <strong>CodeCrafter</strong>. Buona visione! 🍿</p>
        </body>
        </html>
    """

    email_obj = EmailMessage(
        subject,
        html_message,
        'CodeCrafter <no-reply@codecrafter.it>',
        [email]
    )
    email_obj.content_subtype = "html"

    try:
        email_obj.send()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def clear_session(request):
    keys_to_clear = ['film', 'date', 'orario']
    for key in keys_to_clear:
        if key in request.session:
            del request.session[key]
    return HttpResponse("Sessione ripulita")
