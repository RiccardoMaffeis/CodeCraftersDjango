function showCustomAlert (icon, title, text = '') {
  Swal.fire({
    icon,
    title,
    text,
    toast: true,
    position: 'top-end',
    timer: 3000,
    showConfirmButton: false
  })
}

document.addEventListener('DOMContentLoaded', function () {
  const params = new URLSearchParams(window.location.search)

  document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault()

      Swal.fire({
        title: 'Sei sicuro?',
        text: 'Questa operazione non è reversibile!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#aaa',
        confirmButtonText: 'Sì, elimina',
        cancelButtonText: 'Annulla'
      }).then(result => {
        if (result.isConfirmed) {
          form.submit()
        }
      })
    })
  })
})
