// static/app_nav/nav.js
document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('togglebtn')
  const sidebar = document.getElementById('sidebar')
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('expanded')
      toggleBtn.classList.toggle('active')
    })
  }

  const currentPath = window.location.pathname.replace(/\/$/, '')
  document.querySelectorAll('#sidebar nav ul li').forEach(li => {
    li.classList.remove('active')
  })

  document.querySelectorAll('#sidebar nav ul li a').forEach(a => {
    const href = a.getAttribute('href')
    if (!href || href === '#') return

    const linkPath = new URL(a.href, window.location.origin).pathname.replace(
      /\/$/,
      ''
    )
    if (linkPath === currentPath) {
      a.parentElement.classList.add('active')
    }
  })
})

document.addEventListener('DOMContentLoaded', () => {
  const bigliettiLink = document.getElementById('biglietti-link')
  const searchBtn = document.querySelector('.btn-search')
  const bookBtns = document.querySelectorAll('.btn-book')
  const ticketBtns = document.querySelectorAll('.ticket-btn')

  if (localStorage.getItem('bigliettiAttivo') === 'true' && bigliettiLink) {
    bigliettiLink.classList.remove('disabled-link')
  }

  function attivaLinkBiglietti () {
    if (bigliettiLink) {
      bigliettiLink.classList.remove('disabled-link')
      localStorage.setItem('bigliettiAttivo', 'true')
    }
  }

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

let leavingViaLink = false

document.addEventListener('click', e => {
  const target = e.target.closest('a, button')
  if (target && target.href && target.href.startsWith(window.location.origin)) {
    leavingViaLink = true
  }
})

document.addEventListener('submit', e => {
  leavingViaLink = true
})

window.addEventListener('beforeunload', e => {
  if (!leavingViaLink) {
    localStorage.removeItem('bigliettiAttivo')
    navigator.sendBeacon('/biglietti/clear_session/')
  }
})

document.addEventListener('DOMContentLoaded', () => {
  const dbLink = document.getElementById('database-link')

  if (dbLink) {
    dbLink.classList.add('disabled-link')
    dbLink.setAttribute('href', '#')

    if (typeof window.userMail !== 'undefined') {
      const email = window.userMail.trim().toLowerCase()
      if (email === 'admin@gmail.com') {
        dbLink.classList.remove('disabled-link')
        dbLink.setAttribute('href', '/utils/')
      }
    }
  }
})
