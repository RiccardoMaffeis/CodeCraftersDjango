# app_utente/views.py

import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Utente
from app_biglietti.models import Biglietto

@login_required
def profile(request):
    """
    Mostra le informazioni profilo e la lista dei biglietti acquistati dall'utente.
    """
    # Ottieni l’email e il nome direttamente dall’utente autenticato
    nome_utente = request.user.nome
    mail_utente = request.user.email

    # Recupera tutti i biglietti per l’email dell’utente, ordinati per dataVendita desc
    # Usando select_related per ottimizzare l'accesso a proiezione e sala
    tickets_qs = (
        Biglietto.objects
        .filter(email=mail_utente)
        .select_related('proiezione__sala')
        .order_by('-dataVendita')
    )

    context = {
        'tickets': tickets_qs,
        'nome_utente': nome_utente,
        'mail_utente': mail_utente,
    }
    return render(request, 'app_utente/utente.html', context)


@login_required
def elimina_biglietto(request, num_proiezione, num_fila, num_posto):
    """
    Elimina un biglietto corrispondente ai parametri chiave:
    numProiezione, numFila e numPosto.
    Dopo la cancellazione, reindirizza alla pagina profilo con un messaggio flash.
    """
    if request.method == 'POST':
        # Cerca il biglietto con le chiavi primarie e l’email dell’utente
        biglietto = get_object_or_404(
            Biglietto,
            proiezione__numProiezione=num_proiezione,
            numFila=num_fila,
            numPosto=num_posto,
            email=request.user.email
        )
        biglietto.delete()
        messages.success(request, "Biglietto eliminato correttamente.")
    return redirect('app_utente:profile')
