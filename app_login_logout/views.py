# app_login_logout/views.py

import json
from django.http import JsonResponse, HttpResponseBadRequest
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

User = get_user_model()


def auth_view(request):
    """
    Mostra la pagina di login/signup (auth.html).
    Se l’utente è già autenticato, lo reindirizza alla home (app_index:index).
    """
    if request.user.is_authenticated:
        return redirect(reverse("app_index:index"))
    return render(request, "app_login_logout/auth.html")


def login_view(request):
    """
    Gestisce il form HTML di login (POST da auth.html con campi 'email' e 'password').
    Se le credenziali sono corrette, esegue il login e reindirizza alla home.
    Altrimenti, imposta un messaggio di errore e ritorna a auth_view.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            django_login(request, user)
            return redirect(reverse("app_index:index"))
        else:
            messages.error(request, "Email o password non validi.")
    # In ogni altro caso (GET o credenziali sbagliate), torno a auth_view
    return redirect(reverse("app_login_logout:auth"))


@csrf_exempt
def api_login(request):
    """
    Equivalente di auth_login.php:
    - Si aspetta un POST con body JSON: {"mail": "<email>", "password": "<pwd>"}.
    - Controlla le credenziali tramite authenticate().
    - Se corrette, chiama django_login() e restituisce JSON {"success": true, "nome": "<NomeUtente>"}.
    - Altrimenti restituisce JSON {"success": false, "message": "..."}.
    """
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
        # Se il tuo modello User ha un campo “nome”, usalo; altrimenti get_username()
        nome_utente = getattr(user, "first_name", user.get_username())
        return JsonResponse({"success": True, "nome": nome_utente})
    else:
        return JsonResponse({"success": False, "message": "Email o password errati."})


def signup_view(request):
    """
    Gestisce la registrazione (POST da auth.html con campi 'name', 'email', 'password', 'confirm_password').
    Se tutti i controlli passano, crea l’utente e lo logga. Altrimenti reindirizza con messaggi di errore.
    """
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Controllo password
        if password != confirm_password:
            messages.error(request, "Le password non corrispondono.")
            return redirect(reverse("app_login_logout:auth") + "#signup")

        # Controllo esistenza utente con quella email
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email già registrata.")
            return redirect(reverse("app_login_logout:auth") + "#signup")

        # Creo utente
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,  # Se usi un campo “nome” personalizzato, modificalo qui
        )
        django_login(request, user)
        return redirect(reverse("app_index:index"))

    # Se non è POST, torno a auth
    return redirect(reverse("app_login_logout:auth"))


def logout_view(request):
    """
    Esegue il logout e reindirizza alla home.
    """
    if request.user.is_authenticated:
        django_logout(request)
    return redirect(reverse("app_index:index"))

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