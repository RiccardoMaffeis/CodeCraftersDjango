document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM completamente caricato')

  // Inizializza gestione date nei filtri
  inizializzaFormDate()

  // Inizializza gestione del submit del form con AJAX
  inizializzaFormSubmit()

  // Inizializza funzionalità del carosello
  inizializzaCarousel()
})

function inizializzaFormDate () {
  const startDateInput = document.getElementById('start-date')
  const endDateInput = document.getElementById('end-date')
  const form = document.querySelector('.search-form')

  if (startDateInput && endDateInput) {
    // Imposta la data minima di fine uguale a quella di inizio
    startDateInput.addEventListener('change', function () {
      endDateInput.min = this.value || endDateInput.getAttribute('min') || ''
      if (endDateInput.value && endDateInput.value < this.value) {
        endDateInput.value = ''
      }
    })

    // Verifica che la data di fine non sia antecedente all'inizio
    endDateInput.addEventListener('change', function () {
      if (startDateInput.value && this.value < startDateInput.value) {
        showCustomAlert(
          'error',
          'Data non valida',
          'La data finale non può essere precedente a quella iniziale.'
        )
        this.value = ''
        this.focus()
      }
    })

    // Controllo ulteriore al submit del form
    if (form) {
      form.addEventListener('submit', function (e) {
        if (
          startDateInput.value &&
          endDateInput.value &&
          endDateInput.value < startDateInput.value
        ) {
          showCustomAlert(
            'error',
            'Data non valida',
            'La data finale non può essere precedente a quella iniziale.'
          )
          e.preventDefault()
        }
      })
    }
  }
}

function inizializzaFormSubmit () {
  const form = document.getElementById('film-filter-form')
  const container = document.getElementById('movies-container')

  if (!form || !container) return

  // Submit asincrono del form
  form.addEventListener('submit', e => {
    e.preventDefault()

    const params = new URLSearchParams(new FormData(form))
    console.log('Submit film_schedule con params:', params.toString())

    // Chiamata AJAX per ottenere i film filtrati
    fetch(`/film/film_schedule/?${params}`)
      .then(res => {
        console.log('Risposta status:', res.status)
        return res.json()
      })
      .then(data => {
        console.log('Dati ricevuti:', data)
        renderMoviesGrid(data.date_films)
      })
      .catch(err => {
        console.error('Errore nel fetch:', err)
        container.innerHTML =
          '<p class="error">Errore durante il caricamento dei film.</p>'
      })
  })
}

function renderMoviesGrid (dateFilms) {
  const container = document.getElementById('movies-container')
  if (!container) return

  let html = ''

  // Per ogni giorno con film associati
  dateFilms.forEach(group => {
    html += `<div class="day-section"><h3>${group.date}</h3>`
    if (group.films.length > 0) {
      html += `
        <div class="carousel-wrapper">
          <button class="carousel-btn prev" aria-label="Precedente">‹</button>
          <div class="movie-carousel">`

      // Crea una card per ciascun film
      group.films.forEach(film => {
        html += `
          <article class="movie-card">
            <a href="/biglietti/prenota/?film=${
              film.codice
            }&date=${encodeURIComponent(
          group.date
        )}" class="ticket-btn" title="Acquista biglietto">
              <img src="https://cdn-icons-png.flaticon.com/128/3702/3702886.png" alt="Ticket" class="ticket-icon" />
            </a>
            <div class="movie-poster" style="background-image: url('${
              film.imgUrl
            }')"></div>
            <div class="movie-info">
              <h2>${film.titolo}</h2>
            </div>
          </article>`
      })

      html += `
          </div>
          <button class="carousel-btn next" aria-label="Successivo">›</button>
        </div>`
    } else {
      // Nessun film per quel giorno
      html += `<p class="text-muted">Nessun film in programmazione per il giorno ${group.date}.</p>`
    }
    html += `</div>`
  })

  container.innerHTML = html

  // Dopo aver aggiornato il DOM, reinizializza i caroselli
  inizializzaCarousel()
}

function inizializzaCarousel () {
  document.querySelectorAll('.carousel-wrapper').forEach(wrapper => {
    const carousel = wrapper.querySelector('.movie-carousel')
    const prevBtn = wrapper.querySelector('.carousel-btn.prev')
    const nextBtn = wrapper.querySelector('.carousel-btn.next')

    if (!carousel || !prevBtn || !nextBtn) return

    // Calcola lo scroll basato sulla larghezza della card + gap
    const calculateScrollAmount = () => {
      const cards = carousel.querySelectorAll('.movie-card')
      if (cards.length === 0) return 0
      const firstCard = cards[0]
      const style = window.getComputedStyle(carousel)
      const gap = parseFloat(style.gap) || 0
      return firstCard.offsetWidth + gap
    }

    let scrollAmount = calculateScrollAmount()

    // Ricalcola in caso di resize
    window.addEventListener('resize', () => {
      scrollAmount = calculateScrollAmount()
    })

    // Funzione per scrollare il carosello a sinistra o destra
    const scrollCarousel = direction => {
      const currentScroll = carousel.scrollLeft
      const maxScroll = carousel.scrollWidth - carousel.clientWidth

      // Disabilita pulsanti se si raggiungono i limiti
      prevBtn.disabled = direction === -1 && currentScroll <= 0
      nextBtn.disabled = direction === 1 && currentScroll >= maxScroll - 1

      if (!(prevBtn.disabled || nextBtn.disabled)) {
        carousel.scrollBy({
          left: direction * scrollAmount,
          behavior: 'smooth'
        })
      }
    }

    // Eventi click per scorrere
    prevBtn.addEventListener('click', () => scrollCarousel(-1))
    nextBtn.addEventListener('click', () => scrollCarousel(1))

    // Aggiorna stato dei pulsanti durante lo scroll
    carousel.addEventListener(
      'scroll',
      () => {
        const currentScroll = carousel.scrollLeft
        const maxScroll = carousel.scrollWidth - carousel.clientWidth
        prevBtn.disabled = currentScroll <= 0
        nextBtn.disabled = currentScroll >= maxScroll - 1
      },
      { passive: true }
    )

    // Inizializza lo stato dei pulsanti
    carousel.dispatchEvent(new Event('scroll'))
  })
}

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
