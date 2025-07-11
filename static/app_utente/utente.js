document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

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
        if (result.isConfirmed) {
          form.submit();
        }
      });
    });
  });
});