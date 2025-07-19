import json
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from app_utente.models import Utente
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
import secrets
from datetime import timedelta

# Recupera il modello utente attivo (custom o default)
User = get_user_model()

# Vista per mostrare la pagina di login/signup
def auth_view(request):
    if request.user.is_authenticated:
        return redirect(reverse("app_index:index"))
    return render(request, "app_login_logout/auth.html")

# Login classico con redirect
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            django_login(request, user)
            return redirect(reverse("app_index:index"))
        else:
            messages.error(request, "Email o password non validi.")
    return redirect(reverse("app_login_logout:auth"))

# Login via API (JSON) per frontend JS
@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return HttpResponseBadRequest(
            json.dumps({"success": False, "message": "Solo POST consentito."}),
            content_type="application/json",
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
        email = data.get("mail", "").strip()
        password = data.get("password", "")
    except (ValueError, KeyError):
        return JsonResponse(
            {"success": False, "message": "JSON non valido o campi mancanti."},
            status=400,
        )

    if not email or not password:
        return JsonResponse(
            {"success": False, "message": "Email e password sono obbligatori."},
            status=400,
        )

    user = authenticate(request, username=email, password=password)
    if user is not None:
        django_login(request, user)
        nome_utente = getattr(user, "first_name", user.get_username())
        return JsonResponse({"success": True, "nome": nome_utente})
    else:
        return JsonResponse({"success": False, "message": "Email o password errati."})

# Registrazione tramite POST classico (form)
def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password != confirm_password:
            messages.error(request, "Le password non corrispondono.")
            return redirect(reverse("app_login_logout:auth") + "#signup")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email già registrata.")
            return redirect(reverse("app_login_logout:auth") + "#signup")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
        )
        django_login(request, user)
        return redirect(reverse("app_index:index"))

    return redirect(reverse("app_login_logout:auth"))

# Logout: pulisce la sessione e torna alla homepage
def logout_view(request):
    request.session.flush()
    return redirect('app_index:index')

# Login tramite API e modello personalizzato Utente
@csrf_exempt
def auth_login(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Metodo non consentito'}, status=405)

    try:
        data = json.loads(request.body)
        mail = data.get('mail', '').strip()
        password = data.get('password', '')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'success': False, 'message': 'Dati non validi'}, status=400)

    try:
        user = Utente.objects.get(mail=mail)
    except Utente.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Email o password errati'})

    if check_password(password, user.password):
        request.session['user_id'] = user.id
        request.session['nome'] = user.nome
        request.session['mail'] = mail
        return JsonResponse({'success': True, 'nome': user.nome})
    else:
        return JsonResponse({'success': False, 'message': 'Email o password errati'})

# Registrazione tramite API JSON e modello Utente
@csrf_exempt
def auth_register(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Metodo non consentito"}, status=405)

    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        mail = data.get('mail', '').strip()
        password = data.get('password', '')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"success": False, "message": "Dati non validi"}, status=400)

    if not nome or not mail or not password:
        return JsonResponse({"success": False, "message": "Tutti i campi sono obbligatori"}, status=400)

    if Utente.objects.filter(mail=mail).exists():
        return JsonResponse({"success": False, "message": "Email già registrata"}, status=409)

    hashed_password = make_password(password)

    try:
        Utente.objects.create(nome=nome, mail=mail, password=hashed_password)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": "Errore durante la registrazione"}, status=500)

# Recupero password tramite email (con token)
@csrf_exempt
def recover_password(request):
    if request.method != 'POST':
        return JsonResponse({'icon': 'error', 'title': 'Errore', 'message': 'Metodo non consentito'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'icon': 'error', 'title': 'Errore', 'message': 'JSON non valido'}, status=400)

    email = data.get('email', '').strip()
    if not email:
        return JsonResponse({'icon': 'error', 'title': 'Errore', 'message': 'Email mancante'}, status=400)

    try:
        utente = Utente.objects.get(mail=email)
    except Utente.DoesNotExist:
        return JsonResponse({'icon': 'error', 'title': 'Utente non trovato', 'message': 'Nessun account è registrato con questa email'}, status=404)

    token = secrets.token_hex(32)
    expire = timezone.now() + timedelta(hours=1)

    utente.reset_token = token
    utente.reset_expire = expire
    utente.save()

    # Costruisce il link per il reset password con token valido 1 ora
    reset_link = request.build_absolute_uri(reverse('app_login_logout:reset_password', args=[token]))

    subject = "Recupero Password - CodeCrafter"
    message = f"""Ciao {utente.nome},

Abbiamo ricevuto una richiesta per reimpostare la tua password.

Per procedere clicca sul link seguente (valido per 1 ora):
{reset_link}

Se non hai richiesto nulla, puoi ignorare questa email."""

    success = send_mail(
        subject=subject,
        message=message,
        from_email="no-reply@cinecraft.it",
        recipient_list=[email],
        fail_silently=False
    )

    if success:
        return JsonResponse({
            'icon': 'success',
            'title': 'Email inviata',
            'message': 'Controlla la tua casella di posta per reimpostare la password'
        })
    else:
        return JsonResponse({
            'icon': 'error',
            'title': 'Errore invio',
            'message': "Errore durante l'invio dell'email"
        }, status=500)

# Vista per mostrare il form di reset password (dopo aver cliccato il link)
def reset_password_view(request, token):
    try:
        # Verifica che il token sia valido e non scaduto
        user = Utente.objects.get(reset_token=token, reset_expire__gt=timezone.now())
    except Utente.DoesNotExist:
        return HttpResponse("Token non valido o scaduto", status=400)

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if not password or len(password) < 6:
            messages.error(request, "La password deve avere almeno 6 caratteri.")
        elif password != confirm:
            messages.error(request, "Le password non coincidono.")
        else:
            user.password = make_password(password)
            user.reset_token = None
            user.reset_expire = None
            user.save()
            messages.success(request, "Password aggiornata con successo. Ora puoi effettuare il login.")
            return redirect('app_login_logout:login')

    return render(request, 'app_login_logout/reset_password.html', {
        'token': token
    })
