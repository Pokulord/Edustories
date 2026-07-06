import './style.css';

/* ─── Theme Toggle ─────────────────────────────────────────── */
const html = document.documentElement
const themeToggle = document.getElementById('themeToggle')

// Читаем сохранённую тему или системную
const savedTheme = localStorage.getItem('theme')
if (savedTheme === 'light') {
  html.classList.remove('dark')
} else {
  html.classList.add('dark')
}

themeToggle?.addEventListener('click', () => {
  const isDark = html.classList.toggle('dark')
  localStorage.setItem('theme', isDark ? 'dark' : 'light')

  // Fireflies: показываем только в тёмной теме
  const fireflies = document.getElementById('fireflies')
  if (fireflies) {
    fireflies.style.display = isDark ? 'block' : 'none'
  }
})

/* ─── Burger Menu ──────────────────────────────────────────── */
const burger = document.getElementById('burger')
const mobileMenu = document.getElementById('mobileMenu')

burger?.addEventListener('click', () => {
  const isOpen = mobileMenu.classList.contains('opacity-100')
  if (isOpen) {
    mobileMenu.classList.remove('opacity-100', 'pointer-events-auto')
    mobileMenu.classList.add('opacity-0', 'pointer-events-none')
  } else {
    mobileMenu.classList.remove('opacity-0', 'pointer-events-none')
    mobileMenu.classList.add('opacity-100', 'pointer-events-auto')
  }
})

// Закрываем меню при клике на ссылку
mobileMenu?.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    mobileMenu.classList.remove('opacity-100', 'pointer-events-auto')
    mobileMenu.classList.add('opacity-0', 'pointer-events-none')
  })
})

/* ─── Fireflies (dark only) ────────────────────────────────── */
function initFireflies() {
  const container = document.getElementById('fireflies')
  if (!container) return

  // Показываем только в тёмной теме
  const isDark = html.classList.contains('dark')
  container.style.display = isDark ? 'block' : 'none'

  const COUNT = 35

  for (let i = 0; i < COUNT; i++) {
    const fly = document.createElement('div')

    const size = Math.random() * 3 + 2
    const x = Math.random() * 100
    const y = Math.random() * 100
    const duration = Math.random() * 6 + 4
    const delay = Math.random() * 8

    fly.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}%;
      top: ${y}%;
      border-radius: 50%;
      background: radial-gradient(circle, 
        rgba(180,255,180,0.95) 0%, 
        rgba(100,220,130,0.6) 40%, 
        transparent 70%);
      box-shadow: 
        0 0 ${size * 3}px ${size}px rgba(120,255,150,0.5),
        0 0 ${size * 6}px ${size * 2}px rgba(80,200,100,0.2);
      animation: fireflyFloat ${duration}s ease-in-out ${delay}s infinite;
      pointer-events: none;
    `

    container.appendChild(fly)
  }
}

// Инжектируем CSS-анимацию
const style = document.createElement('style')
style.textContent = `
  @keyframes fireflyFloat {
    0%   { transform: translate(0, 0) scale(1);    opacity: 0; }
    15%  { opacity: 1; }
    50%  { transform: translate(
             calc((var(--rx, 1) - 0.5) * 120px),
             calc((var(--ry, 1) - 0.5) * 80px)
           ) scale(1.3); opacity: 0.9; }
    85%  { opacity: 0.6; }
    100% { transform: translate(0, 0) scale(1);    opacity: 0; }
  }
`
document.head.appendChild(style)

// Добавляем случайные CSS-переменные каждому светлячку
document.addEventListener('DOMContentLoaded', () => {
  initFireflies()

  document.querySelectorAll('#fireflies div').forEach(fly => {
    fly.style.setProperty('--rx', String(Math.random()))
    fly.style.setProperty('--ry', String(Math.random()))
  })
})