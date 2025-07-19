// Quando il DOM è completamente caricato...
document.addEventListener('DOMContentLoaded', function () {
  
  // Seleziona tutti i form con classe .delete-form
  document.querySelectorAll('.delete-form').forEach(form => {

    // Aggiunge un event listener sul submit del form
    form.addEventListener('submit', function (e) {
      e.preventDefault(); // Impedisce l'invio immediato del form

      // Mostra una finestra di conferma con SweetAlert2
      Swal.fire({
        title: 'Sei sicuro?',
        text: "Questa operazione non è reversibile!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#aaa',
        confirmButtonText: 'Sì, elimina',
        cancelButtonText: 'Annulla'
      }).then((result) => {
        // Se l'utente conferma, invia il form
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  });
});
