/* =====================================================================
 *  theme.js — универсальный модуль смены темы
 *  Подключать на любой странице: import '/src/theme.js'
 * ===================================================================== */

const THEME_KEY = "witcherAcademyTheme";
const html      = document.documentElement;

/* ─── core ───────────────────────────────────────────────────────── */

function getSavedTheme() {
  return localStorage.getItem(THEME_KEY);
}

function applyTheme(theme) {
  if (theme === "light") {
    html.classList.remove("dark");
  } else {
    html.classList.add("dark");
  }

  localStorage.setItem(THEME_KEY, theme);
  updateToggleUI(theme);
  updateFireflies(theme);
}

function getCurrentTheme() {
  return html.classList.contains("dark") ? "dark" : "light";
}

function toggleTheme() {
  const next = getCurrentTheme() === "dark" ? "light" : "dark";
  applyTheme(next);
}

/* ─── ui: theme toggle button ────────────────────────────────────── */

function updateToggleUI(theme) {
  // Поддерживаем любое кол-во toggle-кнопок на странице
  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    // Можно добавить aria-label
    btn.setAttribute(
      "aria-label",
      theme === "dark" ? "Переключить на светлую тему" : "Переключить на тёмную тему"
    );
  });
}

/* ─── ui: fireflies (только на index) ───────────────────────────── */

function updateFireflies(theme) {
  const fireflies = document.getElementById("fireflies");
  if (!fireflies) return; // на других страницах элемента нет — пропускаем
  fireflies.style.display = theme === "dark" ? "block" : "none";
}

/* ─── bind: кнопки переключения ─────────────────────────────────── */

function bindToggles() {
  // Ищем как по id (обратная совместимость), так и по data-атрибуту
  const byId   = document.getElementById("themeToggle");
  const byAttr = document.querySelectorAll("[data-theme-toggle]");

  function onClick() { toggleTheme(); }

  if (byId && !byId.dataset.themeBound) {
    byId.addEventListener("click", onClick);
    byId.dataset.themeBound = "1";
  }

  byAttr.forEach(function (btn) {
    if (!btn.dataset.themeBound) {
      btn.addEventListener("click", onClick);
      btn.dataset.themeBound = "1";
    }
  });
}

/* ─── init ───────────────────────────────────────────────────────── */

function init() {
  // Применяем сохранённую тему (или dark по умолчанию)
  const saved = getSavedTheme();
  applyTheme(saved === "light" ? "light" : "dark");
  bindToggles();
}

// Запускаем сразу — до DOMContentLoaded чтобы не было вспышки
init();

// Если DOM ещё не готов — перепривязываем кнопки после загрузки
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bindToggles);
}

/* ─── public API ─────────────────────────────────────────────────── */

export { applyTheme, toggleTheme, getCurrentTheme };