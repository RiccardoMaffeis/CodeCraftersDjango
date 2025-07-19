document.addEventListener('DOMContentLoaded', () => {
  // Selezione dei principali elementi DOM per login/signup/recupero password
  const logBtn = document.getElementById('logBtn')
  const signBtn = document.getElementById('signBtn')
  const loginForm = document.getElementById('loginForm')
  const signupForm = document.getElementById('signupForm')
  const forgotForm = document.getElementById('forgotForm')
  const switchToSignup = document.getElementById('switchToSignup')
  const switchToLogin = document.getElementById('switchToLogin')
  const forgotLink = document.getElementById('forgotPasswordLink')

  // Mostra il form di login
  function showLogin () {
    logBtn.classList.add('active')
    signBtn.classList.remove('active')
    loginForm.classList.add('active')
    signupForm.classList.remove('active')
  }

  // Mostra il form di registrazione
  function showSignup () {
    signBtn.classList.add('active')
    logBtn.classList.remove('active')
    signupForm.classList.add('active')
    loginForm.classList.remove('active')
  }

  // Eventi click per passare da login a signup e viceversa
  logBtn.addEventListener('click', showLogin)
  signBtn.addEventListener('click', showSignup)
  switchToSignup?.addEventListener('click', e => {
    e.preventDefault()
    showSignup()
  })
  switchToLogin?.addEventListener('click', e => {
    e.preventDefault()
    showLogin()
  })

  // Se l'URL contiene "#signup", mostra direttamente il form di registrazione
  if (window.location.hash === '#signup') {
    showSignup()
  }

  // Gestione mostra/nascondi password (toggle)
  document.querySelectorAll('.show-password-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = this.parentElement.querySelector('input')
      const isPassword = input.type === 'password'

      input.type = isPassword ? 'text' : 'password'
      this.classList.toggle('active')

      const newLabel = isPassword ? 'Hide password' : 'Show password'
      this.setAttribute('aria-label', newLabel)

      input.focus()
    })
  })

  // ==== REGISTRAZIONE UTENTE ====
  document.getElementById('signupForm').addEventListener('submit', async e => {
    e.preventDefault()
    const inputs = e.target.querySelectorAll(
      'input[type="text"], input[type="email"], input[type="password"]'
    )
    const nome = inputs[0].value.trim()
    const mail = inputs[1].value.trim()
    const password = inputs[2].value
    const confirm = inputs[3].value

    // Verifica che le password coincidano
    if (password !== confirm)
      return showCustomAlert('error', 'Le password non coincidono!')

    // Invia richiesta POST al backend Django per la registrazione
    const res = await fetch('/login/auth_register/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome, mail, password })
    })

    // Parsing della risposta
    const text = await res.text()
    console.log('🔍 RISPOSTA SERVER GREZZA:', text)
    let result
    try {
      result = JSON.parse(text)
    } catch (e) {
      console.error('❌ JSON parse error:', e)
      return
    }

    // Gestione risposta: successo o errore
    if (result.success) {
      showCustomAlert('success', 'Registrazione completata!')
      e.target.reset()
      showLogin()
    } else {
      showCustomAlert(
        'error',
        'Errore nella registrazione: Utente già registrato'
      )
    }
  })

  // ==== LOGIN UTENTE ====
  document.getElementById('loginForm').addEventListener('submit', async e => {
    e.preventDefault()
    const inputs = e.target.querySelectorAll(
      'input[type="text"], input[type="email"], input[type="password"]'
    )
    const mail = inputs[0].value.trim()
    const password = inputs[1].value

    // Invia richiesta POST al backend Django per login
    const res = await fetch('/login/auth_login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mail, password })
    })

    // Parsing risposta
    const text = await res.text()
    console.log('🔍 RISPOSTA SERVER GREZZA:', text)
    let result
    try {
      result = JSON.parse(text)
    } catch (e) {
      console.error('❌ JSON parse error:', e)
      return
    }

    // Se successo, reindirizza alla home; altrimenti mostra errore
    if (result.success) {
      window.location.href = '/'
    } else {
      showCustomAlert('error', 'Errore nel login: Password e/o Mail errata!')
    }
  })

  // ==== RECUPERO PASSWORD ====
  forgotLink?.addEventListener('click', async e => {
    e.preventDefault()

    // Mostra input email con SweetAlert2
    const { value: email } = await Swal.fire({
      title: 'Recupero Password',
      input: 'email',
      inputLabel: 'Inserisci la tua email per ricevere la password',
      inputPlaceholder: 'email@example.com',
      confirmButtonText: 'Invia',
      cancelButtonText: 'Annulla',
      showCancelButton: true,
      heightAuto: false
    })

    if (!email) return

    // Invia richiesta al backend per avviare il recupero password
    try {
      const res = await fetch('/login/recover_password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim() })
      })

      const result = await res.json()
      showCustomAlert(result.icon, result.title, result.message)
    } catch (err) {
      console.error('Errore durante il recupero password:', err)
      showCustomAlert('error', 'Errore', 'Errore durante la richiesta')
    }
  })

  // ==== FUNZIONE GENERICA PER MOSTRARE ALERT CON SWEETALERT ====
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
})
