document.addEventListener("DOMContentLoaded", function () {
    const filmInput = document.getElementById('film');
    const filmIdInput = document.getElementById('film-id');
    const suggestionsContainer = document.getElementById('film-suggestions');
    const salaSelect = document.getElementById('sala');
    const dataSelect = document.getElementById('data');
    const orarioSelect = document.getElementById('orario');
    const submitBtn = document.querySelector('.btn-search');

    salaSelect.disabled = true;
    dataSelect.disabled = true;
    orarioSelect.disabled = true;
    submitBtn.disabled = true;

    function updateSubmitState() {
        submitBtn.disabled = !(
            filmIdInput.value &&
            dataSelect.value &&
            orarioSelect.value
        );
    }

    function aggiornaOpzioni(filmId) {
        if (!filmId) return;

        fetch(`../utils/get_options_by_film.php?film_id=${filmId}`)
            .then(res => res.json())
            .then(data => {
                const formattedDates = data.date.map(d => {
                    const [day, month, year] = d.data.split('/');
                    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
                });

                const today = new Date().toISOString().split('T')[0];

                if (!dataSelect._flatpickr) {
                    flatpickr("#data", {
                        enable: formattedDates,
                        minDate: today,
                        maxDate: "2025-12-31",
                        dateFormat: "Y-m-d",
                        locale: "it"
                    });
                } else {
                    dataSelect._flatpickr.set("enable", formattedDates);
                    dataSelect._flatpickr.set("minDate", today);
                    dataSelect._flatpickr.set("maxDate", "2025-12-31");
                }
                dataSelect.disabled = false;
                updateSubmitState();
            })
            .catch(err => console.error('Errore aggiornaOpzioni:', err));
    }

    dataSelect.addEventListener('change', function () {
        salaSelect.innerHTML = '';
        salaSelect.disabled = true;
        document.getElementById('salaTooltip').style.display = 'none';

        const sel = this.value;
        if (!sel) {
            updateSubmitState();
            return;
        }
        const [y, m, d] = sel.split('-');
        const formattedDate = `${d}/${m}/${y}`;

        fetch(`../utils/get_options_by_film_and_date.php?film_id=${filmInput.dataset.id}&data=${formattedDate}`)
            .then(res => res.json())
            .then(data => {
                orarioSelect.disabled = false;
                orarioSelect.innerHTML = '<option value="">Seleziona un orario</option>';
                data.orari.forEach(o => {
                    const opt = document.createElement('option');
                    opt.value = o.ora;
                    opt.textContent = o.ora.substring(0, 5);
                    orarioSelect.appendChild(opt);
                });
                updateSubmitState();
            })
            .catch(err => console.error('Errore orari:', err));
    });

    orarioSelect.addEventListener('change', function () {
        const selDate = dataSelect.value;
        const selTime = this.value;
        if (!selDate || !selTime) {
            updateSubmitState();
            return;
        }
        const [y, m, d] = selDate.split('-');
        const formattedDate = `${d}/${m}/${y}`;

        fetch(`../utils/get_options_by_film_and_date_and_time.php?film_id=${filmInput.dataset.id}&data=${formattedDate}&ora=${selTime}`)
            .then(res => res.json())
            .then(data => {
                if (data.sale.length) {
                    const info = data.sale[0];
                    let icon = info.tipo === '3-D'
                        ? `<img src="https://cdn-icons-png.flaticon.com/128/83/83596.png" class="sala-icon">`
                        : `<img src="https://cdn-icons-png.flaticon.com/128/83/83467.png" class="sala-icon">`;
                    salaSelect.innerHTML = `Sala ${info.numero} ${icon}`;
                    document.getElementById('sala-hidden').value = info.numero;
                }
                updateSubmitState();
            })
            .catch(err => console.error('Errore sala:', err));
    });

    function renderSuggestions(data) {
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.style.display = 'block';
        document.body.classList.add('no-scroll');

        data.forEach(film => {
            const item = document.createElement('div');
            item.className = 'film-suggestion';
            item.innerHTML = `
                <img src="${film.immagine}" class="film-thumbnail" alt="${film.titolo}">
                <span>${film.titolo}</span>
            `;
            item.dataset.id = film.id;
            suggestionsContainer.appendChild(item);

            item.addEventListener('click', () => {
                filmInput.value = film.titolo;
                filmInput.dataset.id = film.id;
                filmIdInput.value = film.id;

                dataSelect.value = '';
                dataSelect.disabled = true;
                if (dataSelect._flatpickr) {
                    dataSelect._flatpickr.clear();
                    dataSelect._flatpickr.set("enable", []);
                }
                orarioSelect.innerHTML = '<option value="">Seleziona un orario</option>';
                orarioSelect.disabled = true;
                salaSelect.innerHTML = '';
                salaSelect.disabled = true;

                suggestionsContainer.style.display = 'none';
                document.body.classList.remove('no-scroll');

                aggiornaOpzioni(film.id);
                updateSubmitState();
            });
        });
    }

    function mostraTuttiIFilm() {
        fetch('../utils/search_film.php?term=')
            .then(res => res.json())
            .then(renderSuggestions)
            .catch(() => {
                suggestionsContainer.style.display = 'none';
                document.body.classList.remove('no-scroll');
            });
    }

    filmInput.addEventListener('input', function () {
        filmIdInput.value = '';
        updateSubmitState();

        const q = this.value;
        if (!q) {
            mostraTuttiIFilm();
        } else {
            fetch('../utils/search_film.php?term=' + encodeURIComponent(q))
                .then(res => res.json())
                .then(renderSuggestions)
                .catch(() => {
                    suggestionsContainer.style.display = 'none';
                    document.body.classList.remove('no-scroll');
                });
        }
    });

    filmInput.addEventListener('focus', function () {
        if (!this.value) mostraTuttiIFilm();
    });

    document.addEventListener('click', function (e) {
        if (!filmInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
            document.body.classList.remove('no-scroll');
        }
    });

    const form = document.querySelector('.search-form');
    form.addEventListener('submit', function (e) {
        localStorage.setItem('bigliettiAttivo', 'true');
        const raw = dataSelect.value;
        if (raw) {
            const [year, month, day] = raw.split('-');
            dataSelect.value = `${day}/${month}/${year}`;
        }

        const selectedDate = raw;
        const orarioInput = document.querySelector('select[name="orario"], #orario, #orario-select'); 
        const salaDiv = document.getElementById('sala');
        const selectedTime = orarioInput ? orarioInput.value : null;
        const bigliettiLink = document.getElementById('biglietti-link');

        const now = new Date();
        const todayStr = now.toISOString().split('T')[0];
        const nowTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

        if (
            selectedDate === todayStr &&
            selectedTime &&
            selectedTime < nowTime
        ) {
            Swal.fire({
                icon: 'error',
                title: 'Orario non valido',
                text: 'Non puoi selezionare un orario già passato.',
                toast: true,
                position: 'top-end',
                timer: 3000,
                showConfirmButton: false
            });
            e.preventDefault();
            localStorage.removeItem('bigliettiAttivo');
            dataSelect.value = '';
            if (orarioInput) orarioInput.value = '';
            if (salaDiv) salaDiv.innerHTML = '';
            if (bigliettiLink) bigliettiLink.classList.add('disabled-link');
            updateSubmitState();
            return false;
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const carousel = document.querySelector(".movie-carousel");
    const prevBtn = document.querySelector(".carousel-btn.prev");
    const nextBtn = document.querySelector(".carousel-btn.next");
    const scrollAmt = 320;

    prevBtn.addEventListener("click", () => {
        carousel.scrollBy({ left: -scrollAmt, behavior: "smooth" });
    });
    nextBtn.addEventListener("click", () => {
        carousel.scrollBy({ left: scrollAmt, behavior: "smooth" });
    });

    const modal = document.getElementById("movieModal");
    const modalBody = document.getElementById("modalBody");
    const modalClose = document.getElementById("modalClose");

    carousel.addEventListener("click", function (e) {
        const btn = e.target.closest(".btn-details");
        if (!btn) return;
        e.preventDefault();

        const filmId = btn.dataset.filmId;
        const filmDate = btn.dataset.filmDate;
        if (!filmId || !filmDate) return;

        fetch(`../utils/movie_details.php?film_id=${encodeURIComponent(filmId)}&film_date=${encodeURIComponent(filmDate)}`)
            .then(res => {
                if (!res.ok) throw new Error("Network error");
                return res.text();
            })
            .then(html => {
                modalBody.innerHTML = html;
                document.body.classList.add("no-scroll");
                modal.style.display = "flex";
            })
            .catch(() => {
                modalBody.innerHTML = "<p>Errore nel recuperare i dettagli.</p>";
                document.body.classList.add("no-scroll");
                modal.style.display = "flex";
            });
    });

    function closeModal() {
        modal.style.display = "none";
        document.body.classList.remove("no-scroll");
    }
    modalClose.addEventListener("click", closeModal);
    modal.addEventListener("click", e => {
        if (e.target === modal) closeModal();
    });

    const tooltip = document.getElementById("salaTooltip");

    modalBody.addEventListener("mouseover", e => {
        const item = e.target.closest(".showtime-item");
        if (!item) return;

        const d = item.dataset;
        tooltip.innerHTML = `
        <strong>Sala ${d.numero} – ${d.tipo}</strong><br>
        Dimensioni schermo: ${d.dim}"<br>
        Posti totali: ${d.posti}<br>
        File: ${d.file}<br>
        Posti per fila: ${d.postiFila}
      `;
        const rect = item.getBoundingClientRect();
        tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + "px";
        tooltip.style.left = (rect.left + rect.width / 2 - tooltip.offsetWidth / 2) + "px";
        tooltip.style.display = "block";
    });

    modalBody.addEventListener("mouseout", e => {
        if (e.target.closest(".showtime-item")) {
            tooltip.style.display = "none";
        }
    });
});
















