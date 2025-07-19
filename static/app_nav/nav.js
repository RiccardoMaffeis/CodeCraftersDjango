// Quando il DOM è pronto
document.addEventListener('DOMContentLoaded', () => {
  // Toggle apertura/chiusura sidebar
  const toggleBtn = document.getElementById('togglebtn')
  const sidebar = document.getElementById('sidebar')
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('expanded') // Espande o comprime la sidebar
      toggleBtn.classList.toggle('active') // Cambia lo stile del bottone
    })
  }

  // Evidenziazione del link attivo nella sidebar
  const currentPath = window.location.pathname.replace(/\/$/, '') // Rimuove lo slash finale
  document.querySelectorAll('#sidebar nav ul li').forEach(li => {
    li.classList.remove('active') // Rimuove lo stato attivo da tutti i link
  })

  document.querySelectorAll('#sidebar nav ul li a').forEach(a => {
    const href = a.getAttribute('href')
    if (!href || href === '#') return

    // Confronta path del link con URL corrente
    const linkPath = new URL(a.href, window.location.origin).pathname.replace(/\/$/, '')
    if (linkPath === currentPath) {
      a.parentElement.classList.add('active') // Imposta attivo se coincide
    }
  })
})

// Secondo DOMContentLoaded per gestire il link "Acquista biglietti"
document.addEventListener('DOMContentLoaded', () => {
  const bigliettiLink = document.getElementById('biglietti-link')
  const searchBtn = document.querySelector('.btn-search')
  const bookBtns = document.querySelectorAll('.btn-book')
  const ticketBtns = document.querySelectorAll('.ticket-btn')

  // Riattiva link biglietti se presente in localStorage
  if (localStorage.getItem('bigliettiAttivo') === 'true' && bigliettiLink) {
    bigliettiLink.classList.remove('disabled-link')
  }

  // Funzione per attivare il link biglietti e salvare stato in localStorage
  function attivaLinkBiglietti () {
    if (bigliettiLink) {
      bigliettiLink.classList.remove('disabled-link')
      localStorage.setItem('bigliettiAttivo', 'true')
    }
  }

  // Attiva il link quando si effettua una ricerca o clic su pulsanti di prenotazione
  if (searchBtn) {
    searchBtn.addEventListener('click', attivaLinkBiglietti)
  }

  bookBtns.forEach(btn => {
    btn.addEventListener('click', attivaLinkBiglietti)
  })

  ticketBtns.forEach(btn => {
    btn.addEventListener('click', attivaLinkBiglietti)
  })
})

// Variabile globale per controllare se l'utente sta lasciando la pagina tramite link o form
let leavingViaLink = false

// Se l'utente clicca su un link interno o invia un form, imposta la variabile
document.addEventListener('click', e => {
  const target = e.target.closest('a, button')
  if (target && target.href && target.href.startsWith(window.location.origin)) {
    leavingViaLink = true
  }
})

// Imposta leavingViaLink a true anche per i form inviati
document.addEventListener('submit', e => {
  leavingViaLink = true
})

// Prima di lasciare la pagina: se non è tramite link o form, pulisce la sessione
window.addEventListener('beforeunload', e => {
  if (!leavingViaLink) {
    localStorage.removeItem('bigliettiAttivo')
    navigator.sendBeacon('/biglietti/clear_session/')
  }
})

// Gestione visibilità link "Dati generali" solo per admin
document.addEventListener('DOMContentLoaded', () => {
  const dbLink = document.getElementById('database-link')

  if (dbLink) {
    dbLink.classList.add('disabled-link') // Disattiva il link per default
    dbLink.setAttribute('href', '#') // Rende il link non cliccabile

    // Se presente l'email dell'utente nella variabile globale
    if (typeof window.userMail !== 'undefined') {
      const email = window.userMail.trim().toLowerCase()
      if (email === 'admin@gmail.com') {
        // Attiva il link se l'utente è l'admin
        dbLink.classList.remove('disabled-link')
        dbLink.setAttribute('href', '/utils/')
      }
    }
  }
})
