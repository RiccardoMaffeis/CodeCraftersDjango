document.addEventListener('DOMContentLoaded', function () {
  const filmInput = document.getElementById('film')
  const filmIdInput = document.getElementById('film-id')
  const suggestionsContainer = document.getElementById('film-suggestions')
  const salaSelect = document.getElementById('sala')
  const dataSelect = document.getElementById('data')
  const orarioSelect = document.getElementById('orario')
  const submitBtn = document.querySelector('.btn-search')
  let debounceTimeout

  salaSelect.disabled = true
  dataSelect.disabled = true
  orarioSelect.disabled = true
  submitBtn.disabled = true

  function updateSubmitState () {
    submitBtn.disabled = !(
      filmIdInput.value &&
      dataSelect.value &&
      orarioSelect.value
    )
  }

  function aggiornaOpzioni (filmId) {
    if (!filmId) return

    const baseUrl =
      document.getElementById('config').dataset.getOptionsByFilmUrl
    fetch(`${baseUrl}?film_id=${filmId}`)
      .then(res => res.json())
      .then(data => {
        const formattedDates = data.date.map(d => {
          const [day, month, year] = d.data.split('/')
          return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
        })

        const today = new Date().toISOString().split('T')[0]

        if (!dataSelect._flatpickr) {
          flatpickr('#data', {
            enable: formattedDates,
            minDate: today,
            maxDate: '2025-12-31',
            dateFormat: 'Y-m-d',
            locale: 'it'
          })
        } else {
          dataSelect._flatpickr.set('enable', formattedDates)
          dataSelect._flatpickr.set('minDate', today)
          dataSelect._flatpickr.set('maxDate', '2025-12-31')
        }
        dataSelect.disabled = false
        updateSubmitState()
      })
      .catch(err => console.error('Errore aggiornaOpzioni:', err))
  }

  dataSelect.addEventListener('change', function () {
    salaSelect.innerHTML = ''
    salaSelect.disabled = true
    document.getElementById('salaTooltip').style.display = 'none'

    const sel = this.value
    if (!sel) {
      updateSubmitState()
      return
    }
    const [y, m, d] = sel.split('-')
    const formattedDate = `${d}/${m}/${y}`

    const url =
      document.getElementById('config').dataset.getOptionsByFilmAndDateUrl
    fetch(`${url}?film_id=${filmIdInput.value}&data=${formattedDate}`)
      .then(res => res.json())
      .then(data => {
        orarioSelect.disabled = false
        orarioSelect.innerHTML = '<option value="">Seleziona un orario</option>'
        data.orari.forEach(o => {
          const opt = document.createElement('option')
          opt.value = o.ora
          opt.textContent = o.ora.substring(0, 5)
          orarioSelect.appendChild(opt)
        })
        updateSubmitState()
      })
      .catch(err => console.error('Errore orari:', err))
  })

  orarioSelect.addEventListener('change', function () {
    const film = document.getElementById('film-id')
    console.log('Film ID:', film.value)
    const selDate = dataSelect.value
    const selTime = this.value
    if (!selDate || !selTime) {
      updateSubmitState()
      return
    }
    const [y, m, d] = selDate.split('-')
    const formattedDate = `${d}/${m}/${y}`

    const url =
      document.getElementById('config').dataset
        .getOptionsByFilmAndDateAndTimeUrl
    fetch(`${url}?film_id=${film.value}&data=${formattedDate}&ora=${selTime}`)
      .then(res => res.json())
      .then(data => {
        if (data.sale.length) {
          const info = data.sale[0]
          let icon =
            info.tipo === '3-D'
              ? `<img src="https://cdn-icons-png.flaticon.com/128/83/83596.png" class="sala-icon">`
              : `<img src="https://cdn-icons-png.flaticon.com/128/83/83467.png" class="sala-icon">`
          salaSelect.innerHTML = `Sala ${info.numero} ${icon}`
          document.getElementById('sala-hidden').value = info.numero
        }
        updateSubmitState()
      })
      .catch(err => console.error('Errore sala:', err))
  })

  filmInput.addEventListener('input', () => {
    const term = filmInput.value.trim()
    clearTimeout(debounceTimeout)
    debounceTimeout = setTimeout(() => fetchSuggestions(term), 300)
  })

  document.addEventListener('click', e => {
    if (!suggestionsContainer.contains(e.target) && e.target !== filmInput) {
      suggestionsContainer.innerHTML = ''
      suggestionsContainer.style.display = 'none'
    }
  })

  filmInput.addEventListener('focus', () => {
    fetchSuggestions(filmInput.value.trim())
  })

  function fetchSuggestions (term) {
    const config = document.getElementById('config')
    const searchFilmBaseUrl = config.dataset.searchFilmUrl

    const url = new URL(searchFilmBaseUrl, window.location.origin)
    url.searchParams.set('term', term)
    fetch(url)
      .then(resp => {
        if (!resp.ok) throw new Error('HTTP ' + resp.status)
        return resp.json()
      })
      .then(data => renderSuggestions(data))
      .catch(err => {
        console.error('Fetch error:', err)
        suggestionsContainer.innerHTML = ''
        suggestionsContainer.style.display = 'none'
      })
  }

  function renderSuggestions (results) {
    if (!results.length) {
      suggestionsContainer.innerHTML = ''
      suggestionsContainer.style.display = 'none'
      return
    }

    let html = '<ul class="suggestion-list">'
    results.forEach(film => {
      html += `
            <li class="film-suggestion" data-id="${film.id}">
              <img src="${film.immagine}" class="film-thumbnail" alt="${film.titolo}">
              <span class="suggestion-title">${film.titolo}</span>
            </li>
          `
    })
    html += '</ul>'

    suggestionsContainer.innerHTML = html
    suggestionsContainer.style.display = 'block'

    document.querySelectorAll('.film-suggestion').forEach(li => {
      li.addEventListener('click', () => {
        const id = li.getAttribute('data-id')
        const title = li.querySelector('.suggestion-title').innerText

        filmInput.value = title
        filmIdInput.value = id

        suggestionsContainer.innerHTML = ''
        suggestionsContainer.style.display = 'none'

        if (dataSelect._flatpickr) {
          dataSelect._flatpickr.clear()
          dataSelect._flatpickr.set('enable', [])
        }
        dataSelect.value = ''
        orarioSelect.innerHTML = '<option value="">Seleziona un orario</option>'
        salaSelect.innerHTML = ''
        document.getElementById('sala-hidden').value = ''
        dataSelect.disabled = true
        orarioSelect.disabled = true
        salaSelect.disabled = true
        document.getElementById('salaTooltip').style.display = 'none'

        aggiornaOpzioni(id)
        updateSubmitState()
      })
    })
  }

  const form = document.querySelector('.search-form')
  form.addEventListener('submit', function (e) {
    localStorage.setItem('bigliettiAttivo', 'true')

    const selectedFilmId = filmIdInput.value
    const selectedFilmName = filmInput.value
    const selectedDateRaw = dataSelect.value
    const selectedTime = orarioSelect.value
    const salaValue = document.getElementById('sala-hidden').value

    console.log('=== DATI SUBMIT ===')
    console.log('Film ID:', selectedFilmId)
    console.log('Film Name:', selectedFilmName)
    console.log('Data raw:', selectedDateRaw)
    console.log('Orario:', selectedTime)
    console.log('Sala:', salaValue)

    // Controllo validità
    if (!selectedFilmId || !selectedDateRaw || !selectedTime || !salaValue) {
      console.warn('Dati mancanti nel submit. Bloccato.')
      e.preventDefault()
      Swal.fire({
        icon: 'warning',
        title: 'Compila tutti i campi',
        text: 'Assicurati di aver selezionato film, data, orario e sala.'
      })
      return false
    }

    // Controllo orario non passato (oggi)
    const [y, m, d] = selectedDateRaw.split('-')
    const todayStr = new Date().toISOString().split('T')[0]
    const now = new Date()
    const nowTime = `${String(now.getHours()).padStart(2, '0')}:${String(
      now.getMinutes()
    ).padStart(2, '0')}`

    const formattedDate = `${d}/${m}/${y}`
    if (`${y}-${m}-${d}` === todayStr && selectedTime < nowTime) {
      Swal.fire({
        icon: 'error',
        title: 'Orario non valido',
        text: 'Non puoi selezionare un orario già passato.',
        toast: true,
        position: 'top-end',
        timer: 3000,
        showConfirmButton: false
      })
      e.preventDefault()
      localStorage.removeItem('bigliettiAttivo')
      return false
    }

    // Riformatto la data per l’invio nel form (es: 10/07/2025)
    dataSelect.value = formattedDate
  })
})

document.addEventListener('DOMContentLoaded', function () {
  const carousel = document.querySelector('.movie-carousel')
  const prevBtn = document.querySelector('.carousel-btn.prev')
  const nextBtn = document.querySelector('.carousel-btn.next')
  const scrollAmt = 320

  prevBtn.addEventListener('click', () => {
    carousel.scrollBy({ left: -scrollAmt, behavior: 'smooth' })
  })
  nextBtn.addEventListener('click', () => {
    carousel.scrollBy({ left: scrollAmt, behavior: 'smooth' })
  })

  const modal = document.getElementById('movieModal')
  const modalBody = document.getElementById('modalBody')
  const modalClose = document.getElementById('modalClose')
  const tooltip = document.getElementById('salaTooltip')

  function closeModal () {
    modal.style.display = 'none'
    document.body.classList.remove('no-scroll')
  }

  document.querySelectorAll('.btn-details').forEach(btn => {
    btn.addEventListener('click', event => {
      event.preventDefault()
      const filmId = btn.getAttribute('data-film-id')
      const filmDate = btn.getAttribute('data-film-date')
      if (!filmId || !filmDate) return

      const config = document.getElementById('config')
      const baseMovieDetailsUrl = config.dataset.movieDetailsUrl

      const url = `${baseMovieDetailsUrl}?film=${encodeURIComponent(
        filmId
      )}&date=${encodeURIComponent(filmDate)}`

      fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'text/html' }
      })
        .then(response => {
          if (!response.ok) throw new Error('HTTP error: ' + response.status)
          return response.text()
        })
        .then(htmlFragment => {
          modalBody.innerHTML = htmlFragment
          document.body.classList.add('no-scroll')
          modal.style.display = 'flex'
        })
        .catch(error => {
          console.error('Fetch error:', error)
          Swal.fire({
            icon: 'error',
            title: 'Errore',
            text: 'Errore nel recuperare i dettagli.'
          })
        })
    })
  })

  modalClose.addEventListener('click', closeModal)
  modal.addEventListener('click', e => {
    if (e.target === modal) closeModal()
  })

  modalBody.addEventListener('mouseover', e => {
    const item = e.target.closest('.showtime-item')
    if (!item) return

    const d = item.dataset
    tooltip.innerHTML = `
            <strong>Sala ${d.numero} – ${d.tipo}</strong><br>
            Dimensioni schermo: ${d.dim}"<br>
            Posti totali: ${d.posti}<br>
            File: ${d.file}<br>
            Posti per fila: ${d.postiFila}
        `
    const rect = item.getBoundingClientRect()
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px'
    tooltip.style.left =
      rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + 'px'
    tooltip.style.display = 'block'
  })

  modalBody.addEventListener('mouseout', e => {
    if (e.target.closest('.showtime-item')) {
      tooltip.style.display = 'none'
    }
  })
})
