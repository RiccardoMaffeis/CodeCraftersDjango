import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, BadHeaderError
from django.utils.html import format_html

# Vista per gestire l'iscrizione alla newsletter via POST
@csrf_exempt  # Disattiva la protezione CSRF per chiamate API (va usato con cautela)
def subscribe_newsletter(request):
    # Verifica che il metodo HTTP sia POST, altrimenti ritorna errore
    if request.method != 'POST':
        return HttpResponseBadRequest(json.dumps({'status': 'invalid_method'}), content_type='application/json')

    try:
        # Tenta di decodificare il corpo della richiesta come JSON e recuperare l'email
        data = json.loads(request.body)
        email = data.get('email', '').strip()
    except (json.JSONDecodeError, KeyError):
        # Errore nel parsing del JSON o chiave mancante
        return HttpResponseBadRequest(json.dumps({'status': 'invalid_email'}), content_type='application/json')

    # Import dei validatori email
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        # Valida la correttezza sintattica dell'email
        validate_email(email)
    except ValidationError:
        # Email non valida
        return HttpResponseBadRequest(json.dumps({'status': 'invalid_email'}), content_type='application/json')

    # Definizione del contenuto della mail di benvenuto
    subject = "🎉 Benvenuto nella Newsletter di CodeCrafter!"
    html_message = format_html("""
        <html>
        <body>
          <h2 style="color:#580000;">Grazie per esserti iscritto!</h2>
          <p>Hai appena ricevuto le ultime novità e promozioni di <strong>CodeCrafter</strong> direttamente nella tua casella.</p>
          <p style="margin-top:20px;">Buona visione e a presto! 🍿</p>
        </body>
        </html>
    """)
    from_email = "CodeCrafter <no-reply@codecrafter.it>"

    try:
        # Invio dell'email al destinatario
        send_mail(
            subject=subject,
            message="",  # Nessun messaggio testuale semplice, solo HTML
            from_email=from_email,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False  # Genera eccezione in caso di errore
        )
        # Risposta OK in formato JSON
        return JsonResponse({'status': 'ok'})
    except BadHeaderError:
        # Errore nell'intestazione dell'email
        return HttpResponseServerError(json.dumps({'status': 'error'}), content_type='application/json')
    except Exception:
        # Qualsiasi altro errore generico
        return HttpResponseServerError(json.dumps({'status': 'error'}), content_type='application/json')


# Vista per visualizzare la pagina database.html e controllare accesso admin
def database_view(request):
    # Recupera la mail salvata nella sessione
    mail = request.session.get('mail', '')
    # Controlla se l'utente è admin
    is_admin = (mail == 'admin@gmail.com')

    # Renderizza il template 'database.html' passando il flag is_admin
    return render(request, 'app_database/database.html', {
        'is_admin': is_admin
    })
