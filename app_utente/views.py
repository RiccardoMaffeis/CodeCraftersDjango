# app_utente/views.py
from django.shortcuts import render, redirect, get_object_or_404

from app_film.models import Proiezione
from app_biglietti.models import Biglietto

# Vista per mostrare il profilo dell'utente con i suoi biglietti
def profile(request):
    # Se l'utente non è autenticato (nessuna mail nella sessione), reindirizza alla pagina di login
    if 'mail' not in request.session:
        return redirect('app_login_logout:auth')

    # Recupera mail e nome dalla sessione
    mail_utente = request.session['mail']
    nome_utente = request.session.get('nome', '')

    # Recupera tutti i biglietti dell'utente ordinati per data di vendita decrescente
    tickets_raw = (
        Biglietto.objects
        .filter(email=mail_utente)
        .order_by('-datavendita')
    )

    enriched_tickets = []
    for b in tickets_raw:
        # Recupera la proiezione associata al biglietto
        proiezione = Proiezione.objects.filter(numproiezione=b.numproiezione).first()
        # Recupera la sala dalla proiezione (se esiste)
        sala = proiezione.sala if proiezione and proiezione.sala else None
        # Costruisce un dizionario con informazioni arricchite
        enriched_tickets.append({
            'biglietto': b,
            'proiezione': proiezione,
            'sala': sala
        })

    # Recupera e rimuove eventuale flag di "biglietto eliminato" dalla sessione
    deleted_flag = request.session.pop('deleted_ticket', False)

    # Passa il contesto al template utente.html
    context = {
        'tickets': enriched_tickets,
        'nome_utente': nome_utente,
        'mail_utente': mail_utente,
        'deleted_ticket': deleted_flag,
    }
    return render(request, 'app_utente/utente.html', context)


# Vista per eliminare un biglietto (richiamata da form POST)
def elimina_biglietto(request, num_proiezione, num_fila, num_posto):
    # Verifica che il metodo sia POST e che l'utente sia autenticato
    if request.method == 'POST' and 'mail' in request.session:
        email_utente = request.session['mail']

        # Recupera il biglietto da eliminare o restituisce errore 404 se non trovato
        biglietto = get_object_or_404(
            Biglietto,
            numproiezione=num_proiezione,
            numfila=num_fila,
            numposto=num_posto,
            email=email_utente
        )
        # Elimina il biglietto
        biglietto.delete()

        # Imposta un flag nella sessione per indicare che un biglietto è stato eliminato
        request.session['deleted_ticket'] = True

    # Reindirizza alla pagina profilo
    return redirect('app_utente:profile')
