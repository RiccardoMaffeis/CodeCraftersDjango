// Quando il DOM è completamente caricato
document.addEventListener('DOMContentLoaded', function () {
  // Riferimenti al form della newsletter e all'input email
  const form  = document.getElementById('newsletter-form');
  const email = document.getElementById('newsletter-email');

  // Gestione dell'invio del form
  form.addEventListener('submit', function (e) {
    e.preventDefault(); // Previene l'invio standard del form

    const address = email.value.trim(); // Rimuove spazi vuoti

    // Validazione: email vuota
    if (!address) {
      Swal.fire({
        icon: 'error',
        title: 'Email non valida',
        text: 'Per favore inserisci un indirizzo email valido.',
        toast: true,
        position: 'top-end',
        timer: 3000,
        showConfirmButton: false
      });
      return;
    }

    // Invio della richiesta POST al backend per iscrizione newsletter
    fetch('/utils/subscribe_newsletter/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: address })
    })
    .then(res => res.json().then(body => ({ status: res.status, body }))) // Parsing della risposta
    .then(({ status, body }) => {
      // Successo: email registrata
      if (status === 200 && body.status === 'ok') {
        Swal.fire({
          icon: 'success',
          title: 'Iscrizione avvenuta con successo',
          text: 'Grazie per esserti iscritto alla nostra newsletter!',
          toast: true,
          position: 'top-end',
          timer: 3000,
          showConfirmButton: false
        });
        form.reset(); // Pulisce il campo email

      // Errore: email non valida (controllo lato server)
      } else if (status === 400 && body.status === 'invalid_email') {
        Swal.fire({
          icon: 'error',
          title: 'Email non valida',
          text: 'Controlla e riprova.',
          toast: true,
          position: 'top-end',
          timer: 3000,
          showConfirmButton: false
        });

      // Errore generico del server
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Errore',
          text: 'Errore durante l\'iscrizione. Riprova più tardi.',
          toast: true,
          position: 'top-end',
          timer: 3000,
          showConfirmButton: false
        });
      }
    })
    .catch(err => {
      // Gestione errore di rete o JSON malformato
      console.error('Network or parsing error:', err);
      Swal.fire({
        icon: 'error',
        title: 'Errore di rete',
        text: 'Impossibile contattare il server. Riprova più tardi.',
        toast: true,
        position: 'top-end',
        timer: 3000,
        showConfirmButton: false
      });
    });
  });
});
