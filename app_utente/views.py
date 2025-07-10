# app_utente/views.py

import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from app_film.models import Proiezione
from .models import Utente
from app_biglietti.models import Biglietto

def profile(request):
    if 'mail' not in request.session:
        return redirect('app_login_logout:auth')

    mail_utente = request.session['mail']
    nome_utente = request.session.get('nome', '')

    tickets_qs = (
        Biglietto.objects
        .filter(email=mail_utente)
        .order_by('-datavendita')
    )

    # Recupera e rimuovi il flag dalla sessione
    deleted_flag = request.session.pop('deleted_ticket', False)

    context = {
        'tickets': tickets_qs,
        'nome_utente': nome_utente,
        'mail_utente': mail_utente,
        'deleted_ticket': deleted_flag,  # nuovo
    }
    return render(request, 'app_utente/utente.html', context)


def elimina_biglietto(request, num_proiezione, num_fila, num_posto):
    if request.method == 'POST' and 'mail' in request.session:
        email_utente = request.session['mail']

        biglietto = get_object_or_404(
            Biglietto,
            numproiezione=num_proiezione,
            numfila=num_fila,
            numposto=num_posto,
            email=email_utente
        )
        biglietto.delete()

        # Salva un flag nella sessione
        request.session['deleted_ticket'] = True

    return redirect('app_utente:profile')
