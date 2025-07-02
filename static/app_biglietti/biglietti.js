document.addEventListener('DOMContentLoaded', function () {

  const urlParams = new URLSearchParams(window.location.search);
  const date = urlParams.get('date');
  const orarioInUrl = urlParams.get('orario');
  const salaInUrl = urlParams.get('sala');
  const filmParams = urlParams.getAll('film');
  const filmId = filmParams[filmParams.length - 1];

  const SEAT_TYPES = {
    VIP: { price: 18, class: 'vip' },
    STANDARD: { price: 12, class: 'standard' }
  };

  const PROMO_CODES = {
    'CINEMA20': 20,
    'PREMIUM35': 35,
    'FESTA10': 10
  };

  const bookingState = {
    selectedTime: null,
    selectedSeats: [],
    totalPrice: 0,
    discountApplied: 0,
    currentStep: 1,
    maxStep: 1
  };

  const ui = {
    steps: document.querySelectorAll('.booking-steps .step'),
    timeSlots: document.querySelectorAll('.time-slot'),
    sections: {
      1: document.querySelector('.row-top'),
      2: document.querySelector('.row-middle'),
      3: document.querySelector('.row-bottom')
    },
    seatsGrid: document.querySelector('.seats-grid'),
    seatsList: document.querySelector('.selected-seats'),
    totalEl: document.getElementById('total'),
    promoInput: document.querySelector('.promo-section input'),
    applyPromo: document.querySelector('.apply-promo'),
    checkoutBtn: document.querySelector('.checkout-button')
  };

  disablePastTimesIfToday();

  function updateSteps(targetStep) {
    if (targetStep > bookingState.maxStep) {
      bookingState.maxStep = targetStep;
    }
    bookingState.currentStep = targetStep;

    [1, 2, 3].forEach(i => {
      ui.sections[i].style.display = (i <= bookingState.maxStep ? '' : 'none');
    });

    ui.steps.forEach((el, idx) => {
      const stepNum = idx + 1;
      el.classList.toggle('active', stepNum === targetStep);
      el.classList.toggle('completed', stepNum < targetStep);
    });
  }

  ui.steps.forEach((el, idx) => {
    el.addEventListener('click', () => {
      const clicked = idx + 1;
      if (clicked < bookingState.currentStep) {
        bookingState.selectedSeats = [];
        bookingState.totalPrice = 0;
        bookingState.discountApplied = 0;
        document.querySelectorAll('.seat.selected').forEach(s => s.classList.remove('selected'));
        updateCart();
        updateSteps(clicked);
      }
    });
  });

  updateSteps(1);

  ui.timeSlots.forEach(slot => {
    slot.addEventListener('click', () => {
      resetCart();
      ui.timeSlots.forEach(s => s.classList.remove('selected'));
      slot.classList.add('selected', 'rubberBand');

      const fullTime = slot.getAttribute('data-time');
      const orario = fullTime.slice(0, 5);
      bookingState.selectedTime = orario;

      const url = new URL(window.location.href);
      const filmParams = urlParams.getAll('film');
      const filmId = filmParams[filmParams.length - 1];
      const date = urlParams.get('date');
      const oraCompleta = orario.includes(':00') ? orario : `${orario}:00`;
      fetch(`../utils/get_proiezione_id.php?film=${filmId}&data=${date}&ora=${oraCompleta}`)
        .then(res => { if (!res.ok) throw new Error(res.status); return res.json(); })
        .then(data => {
          if (!data?.sala) {
            showCustomAlert('error', 'Sala non trovata per questo orario');
            return;
          }
          const sala = data.sala;
          url.searchParams.set('orario', orario);
          url.searchParams.set('sala', sala);
          fetch('../utils/salva_parametri.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ orario, sala })
          }).finally(() => history.replaceState(null, '', url));
          document.getElementById('sala').textContent = sala;
          generateSeatsFromSala(sala);
          updateSteps(2);
        })
        .catch(err => {
          console.error(err);
          showCustomAlert('error', 'Errore nel caricamento della sala');
        });
    });
  });

  function generateSeatsFromSala(salaId) {
    fetch(`../utils/get_sala_data.php?id=${salaId}`)
      .then(res => res.json())
      .then(data => {
        if (data.numFile && data.numPostiPerFila) {
          generateSeats(data.numFile, data.numPostiPerFila);
        } else {
          console.error('Dati sala non validi', data);
          showCustomAlert('error', 'Errore dati sala');
        }
      })
      .catch(err => {
        console.error(err);
        showCustomAlert('error', 'Errore durante il caricamento della sala');
      });
  }

  function generateSeats(numRighe, numColonne) {
    getOccupiedSeats().then(occupied => {
      ui.seatsGrid.style.setProperty('--cols', numColonne);
      ui.seatsGrid.innerHTML = '';

      for (let riga = 0; riga < numRighe; riga++) {
        for (let col = 0; col < numColonne; col++) {
          const seatNumber = `${String.fromCharCode(65 + riga)}${col + 1}`;
          const seatEl = createSeatElement(seatNumber, occupied, riga, numRighe);
          ui.seatsGrid.appendChild(seatEl);
        }
      }

      animateElements('.seat', 'bounceIn');
    });
  }

  function caricaSalaEGeneraPosti() {
    const salaId = urlParams.get('sala');
    if (!salaId) return;
    document.getElementById('sala').textContent = salaId;
    generateSeatsFromSala(salaId);
  }

  function createSeatElement(seatNumber, occupiedSeats, riga, numRighe) {
    const isVIP = riga >= numRighe - 2;
    const type = isVIP ? SEAT_TYPES.VIP : SEAT_TYPES.STANDARD;
    const seat = document.createElement('div');
    const occupied = occupiedSeats.includes(seatNumber);

    seat.className = `seat ${type.class} ${occupied ? 'occupied' : 'available'}`;
    seat.textContent = seatNumber;
    seat.title = `Posto ${type.class.toUpperCase()} - €${type.price}`;
    seat.setAttribute('data-seat-number', seatNumber);
    if (!occupied) {
      seat.addEventListener('click', () => toggleSeatSelection(seat, seatNumber, type.price));
    }
    return seat;
  }

  function toggleSeatSelection(seat, seatNumber, price) {
    seat.classList.toggle('selected');
    if (seat.classList.contains('selected')) {
      bookingState.selectedSeats.push({ number: seatNumber, price });
      bookingState.totalPrice += price;
    } else {
      bookingState.selectedSeats = bookingState.selectedSeats.filter(s => s.number !== seatNumber);
      bookingState.totalPrice -= price;
    }
    if (bookingState.selectedSeats.length > 0 && bookingState.currentStep < 3) {
      updateSteps(3);
    }
    if (bookingState.selectedSeats.length === 0 && bookingState.currentStep === 3) {
      updateSteps(2);
    }
    updateCart();
  }

  function updateCart() {
    if (bookingState.selectedSeats.length === 0) {
      bookingState.discountApplied = 0;
      if (ui.promoInput.value !== '') ui.promoInput.value = '';
      ui.promoInput.disabled = false;
      ui.applyPromo.disabled = false;
    } else if (bookingState.selectedSeats.length >= 10) {
      if (ui.promoInput.value !== 'CINEMA20') {
        ui.promoInput.value = 'CINEMA20';
        showCustomAlert('success', 'Sconto 20% per 10 o più biglietti!');
        animateElements('.promo-section', 'heartBeat');
      }
      ui.promoInput.disabled = true;
      ui.applyPromo.disabled = true;
      bookingState.discountApplied = PROMO_CODES['CINEMA20'];
    } else {
      const code = ui.promoInput.value.toUpperCase();
      const manualDiscount = PROMO_CODES[code] || 0;
      if (
        manualDiscount > 0 &&
        code !== 'CINEMA20' &&
        code !== 'LOGIN10'
      ) {
        bookingState.discountApplied = manualDiscount;
        ui.promoInput.disabled = false;
        ui.applyPromo.disabled = false;
      } else if (typeof userMail !== 'undefined' && userMail) {
        if (ui.promoInput.value !== 'LOGIN10') {
          ui.promoInput.value = 'LOGIN10';
          showCustomAlert('success', 'Sconto 10% per utenti registrati!');
          animateElements('.promo-section', 'heartBeat');
        }
        ui.promoInput.disabled = true;
        ui.applyPromo.disabled = true;
        bookingState.discountApplied = 10;
      } else {
        bookingState.discountApplied = 0;
        if (ui.promoInput.value !== '') ui.promoInput.value = '';
        ui.promoInput.disabled = false;
        ui.applyPromo.disabled = false;
      }
    }

    ui.seatsList.innerHTML = bookingState.selectedSeats
      .map(s => `<li>Posto ${s.number} (€${s.price})</li>`).join('');
    const discounted = bookingState.totalPrice * (1 - bookingState.discountApplied / 100);
    ui.totalEl.textContent = discounted.toFixed(2);
  }

  function getOccupiedSeats() {
    const filmParams = urlParams.getAll('film');
    const filmId = filmParams.length ? filmParams[filmParams.length - 1] : null;
    const date = urlParams.get('date');
    const ora = bookingState.selectedTime
      ? bookingState.selectedTime + ':00'
      : urlParams.get('orario');
    if (!filmId || !date || !ora) return Promise.resolve([]);
    return fetch(`../utils/get_proiezione_id.php?film=${filmId}&data=${date}&ora=${ora}`)
      .then(r => r.json())
      .then(d => {
        if (!d.proiezioneId) return [];
        return fetch(`../utils/get_posti_occupati.php?proiezione=${d.proiezioneId}`)
          .then(r => r.json());
      })
      .catch(err => {
        console.error(err);
        return [];
      });
  }

  ui.applyPromo.addEventListener('click', () => {
    const code = ui.promoInput.value.toUpperCase();
    const disc = PROMO_CODES[code] || 0;
    if (disc > 0) {
      bookingState.discountApplied = disc;
      updateCart();
      showCustomAlert('success', `Sconto ${disc}% applicato!`);
      animateElements('.promo-section', 'heartBeat');
    } else {
      showCustomAlert('error', 'Codice promozionale non valido');
    }
  });

  ui.checkoutBtn.addEventListener('click', () => {
    if (!bookingState.selectedTime || bookingState.selectedSeats.length === 0) {
      showCustomAlert('warning', 'Completa tutti i passaggi!', 'Seleziona orario e posti');
      return;
    }
    const filmTitle = document.querySelector('.movie-title span')?.textContent.trim() || '';
    const conferma = `📽️ Film: ${filmTitle}<br>⏰ Orario: ${bookingState.selectedTime}` +
      `<br>💺 Posti: ${bookingState.selectedSeats.map(s => s.number).join(', ')}` +
      `<br>💰 Totale: €${(bookingState.totalPrice * (1 - bookingState.discountApplied / 100)).toFixed(2)}`;

    Swal.fire({
      title: 'Confermare la prenotazione?',
      html: conferma,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Conferma',
      cancelButtonText: 'Annulla'
    }).then(res => {
      if (!res.isConfirmed) return;
      const filmParams = urlParams.getAll('film');
      const filmId = filmParams[filmParams.length - 1];
      const date = urlParams.get('date');
      let ora = bookingState.selectedTime;
      if (ora && !ora.includes(':00')) ora += ':00';
      fetch(`../utils/get_proiezione_id.php?film=${filmId}&data=${date}&ora=${ora}`)
        .then(r => r.json())
        .then(d => {
          const pid = d.proiezioneId;
          const askMail = () => {
            Swal.fire({
              title: 'Inserisci la tua email',
              input: 'email',
              inputLabel: 'Riceverai il riepilogo',
              inputPlaceholder: 'email@example.com',
              showCancelButton: true,
              confirmButtonText: 'Invia'
            }).then(input => {
              if (input.isConfirmed && input.value) {
                salvaBigliettiEInvia(input.value, filmTitle, pid);
              }
            });
          };
          if (typeof userMail !== 'undefined' && userMail) {
            salvaBigliettiEInvia(userMail, filmTitle, pid);
          } else {
            askMail();
          }
        })
        .catch(err => {
          console.error(err);
          showCustomAlert('error', 'Errore di rete o server');
        });
    });
  });

  function resetCart() {
    bookingState.selectedSeats = [];
    bookingState.totalPrice = 0;
    bookingState.discountApplied = 0;
    document.querySelectorAll('.seat.selected').forEach(s => s.classList.remove('selected'));
    updateCart();
  }

  function salvaBigliettiEInvia(email, filmTitle, proiezioneId) {
    fetch('../utils/salva_biglietti.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        proiezioneId,
        posti: bookingState.selectedSeats.map(s => s.number),
        prezzi: bookingState.selectedSeats.map(s => s.price),
        mail: email
      })
    })
      .then(r => r.json())
      .then(resp => {
        if (resp.status === 'ok') {
          inviaMail(email, filmTitle);
        } else {
          showCustomAlert('error', 'Errore durante il salvataggio dei biglietti');
        }
      })
      .catch(err => {
        console.error(err);
        showCustomAlert('error', 'Errore di rete o server');
      });
  }

  function inviaMail(email, film) {
    const payload = {
      email,
      film,
      orario: bookingState.selectedTime,
      posti: bookingState.selectedSeats.map(s => s.number).join(', '),
      totale: (bookingState.totalPrice * (1 - bookingState.discountApplied / 100)).toFixed(2)
    };
    fetch('../utils/send_ticket_email.php', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(r => r.json())
      .then(data => {
        if (data.status === 'ok') {
          Swal.fire({
            title: 'Prenotazione Confermata! 🎉',
            html: 'Riceverai una mail di conferma<br>Buona visione!',
            icon: 'success',
            timer: 3000,
            showConfirmButton: false,
            willClose: () => {
              localStorage.removeItem('bigliettiAttivo');
              navigator.sendBeacon('../utils/clear_session.php');
              window.location.href = '../index/index.php';
            }
          });
        } else {
          showCustomAlert('error', 'Errore nell’invio della mail');
        }
      });
  }

  function disablePastTimesIfToday() {
    const selectedDate = date;
    if (!selectedDate) return;

    const [gg, mm, aaaa] = selectedDate.split('/');

    const today = new Date();
    const isToday =
      today.getDate() === +gg &&
      today.getMonth() === +mm - 1 &&
      today.getFullYear() === +aaaa;

    if (isToday) {
      const nowMinutes = today.getHours() * 60 + today.getMinutes();

      ui.timeSlots.forEach(slot => {
        const timeStr = slot.getAttribute('data-time');
        if (timeStr) {
          const [hh, min] = timeStr.split(':').map(Number);
          const slotMinutes = hh * 60 + min;
          if (slotMinutes <= nowMinutes) {
            slot.classList.add('disabled');
            slot.style.pointerEvents = 'none';
            slot.style.opacity = 0.4;
          }
        }
      });
    }
  }

  function animateElements(selector, animation) {
    document.querySelectorAll(selector).forEach(el => {
      el.style.animation = `${animation} 0.5s ease-out`;
      el.addEventListener('animationend', () => el.style.animation = '');
    });
  }
  function showCustomAlert(icon, title, text = '') {
    Swal.fire({ icon, title, text, toast: true, position: 'top-end', timer: 3000, showConfirmButton: false });
  }

  caricaSalaEGeneraPosti();

  if (orarioInUrl && salaInUrl && filmId && date) {
    ui.timeSlots.forEach(slot => {
      if (slot.getAttribute('data-time')?.startsWith(orarioInUrl)) {
        slot.classList.add('selected');
      }
    });

    bookingState.selectedTime = orarioInUrl;

    document.getElementById('sala').textContent = salaInUrl;
    generateSeatsFromSala(salaInUrl);
    updateSteps(2);
  }
});
