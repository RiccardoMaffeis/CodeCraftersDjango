# app_database/views.py

from django.shortcuts import render

def dashboard_view(request):
    # Controlla se l’utente è amministratore (ad es. email admin@gmail.com)
    is_admin = request.user.is_authenticated and request.user.email == 'admin@gmail.com'

    return render(request, 'app_database/dashboard.html', {
        'is_admin': is_admin
    })
