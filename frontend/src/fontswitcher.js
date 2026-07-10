/* =====================================================================
 *  fontswitcher.js
 * ===================================================================== */

const FONT_KEY    = "witcherAcademyFont";
const DEFAULT_FONT = "classic";

const FONTS = {
  classic:   { label: "Классический",  description: "Cormorant + PT Serif" },
  chronicle: { label: "Летописный",    description: "Ruslan Display + Alegreya" },
  noble:     { label: "Благородный",   description: "Playfair Display + Lora" },
};

/* ─── core ───────────────────────────────────────────────────────── */

function getFont() {
  return localStorage.getItem(FONT_KEY) || DEFAULT_FONT;
}

function applyFont(fontKey) {
  const key = FONTS[fontKey] ? fontKey : DEFAULT_FONT;

  // Ставим на <html> — именно туда смотрит CSS селектор [data-font="..."]
  document.documentElement.setAttribute("data-font", key);
  localStorage.setItem(FONT_KEY, key);
  updateSwitcherUI(key);

  // Дебаг — убери после проверки
  console.log("[FontSwitcher] applied:", key, document.documentElement.getAttribute("data-font"));
}

/* ─── UI ─────────────────────────────────────────────────────────── */

function buildSwitcher() {
  // Не строим дважды
  if (document.getElementById("fontSwitcher")) return;

  const container = document.createElement("div");
  container.id = "fontSwitcher";
  container.className = "fixed bottom-6 right-6 z-50 flex flex-col items-end gap-2";

  /* Триггер */
  const trigger = document.createElement("button");
  trigger.id = "fontSwitcherTrigger";
  trigger.type = "button";
  trigger.setAttribute("aria-label", "Сменить шрифт");
  trigger.className = [
    "w-10 h-10 rounded-full flex items-center justify-center",
    "bg-emerald-900/80",
    "border border-emerald-700/40",
    "text-emerald-300",
    "shadow-lg transition hover:scale-110 text-base font-semibold",
  ].join(" ");
  trigger.textContent = "Aa";

  /* Панель */
  const panel = document.createElement("div");
  panel.id = "fontSwitcherPanel";
  panel.className = [
    "hidden flex-col gap-1 p-3 rounded-xl",
    "bg-[#071312]/95 backdrop-blur-xl",
    "border border-emerald-900/60",
    "shadow-2xl",
    "min-w-[200px]",
  ].join(" ");

  /* Заголовок панели */
  const title = document.createElement("p");
  title.className = "text-[10px] uppercase tracking-widest mb-2 text-emerald-400/60";
  title.textContent = "Стиль шрифта";
  panel.appendChild(title);

  /* Кнопки вариантов */
  Object.entries(FONTS).forEach(([key, meta]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.dataset.fontKey = key;
    btn.className = [
      "font-option-btn",
      "flex flex-col items-start px-3 py-2 rounded-lg w-full text-left",
      "transition duration-200",
      "hover:bg-emerald-900/40",
    ].join(" ");

    const labelEl = document.createElement("span");
    labelEl.className = "text-sm text-emerald-200 font-semibold";
    labelEl.textContent = meta.label;

    const descEl = document.createElement("span");
    descEl.className = "text-[10px] text-emerald-400/60";
    descEl.textContent = meta.description;

    btn.appendChild(labelEl);
    btn.appendChild(descEl);

    btn.addEventListener("click", () => {
      applyFont(key);
      closePanel();
    });

    panel.appendChild(btn);
  });

  container.appendChild(panel);
  container.appendChild(trigger);
  document.body.appendChild(container);

  /* Открытие/закрытие */
  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    panel.classList.contains("hidden") ? openPanel() : closePanel();
  });

  document.addEventListener("click", (e) => {
    if (!container.contains(e.target)) closePanel();
  });
}

function openPanel() {
  const panel = document.getElementById("fontSwitcherPanel");
  if (!panel) return;
  panel.classList.remove("hidden");
  panel.classList.add("flex");
}

function closePanel() {
  const panel = document.getElementById("fontSwitcherPanel");
  if (!panel) return;
  panel.classList.add("hidden");
  panel.classList.remove("flex");
}

function updateSwitcherUI(activeKey) {
  document.querySelectorAll(".font-option-btn").forEach((btn) => {
    const isActive = btn.dataset.fontKey === activeKey;
    // Активный элемент — подсветка
    btn.classList.toggle("bg-emerald-900/60", isActive);
    btn.classList.toggle("ring-1",            isActive);
    btn.classList.toggle("ring-emerald-500/40", isActive);
  });
}

/* ─── init ───────────────────────────────────────────────────────── */

function init() {
  // Сначала применяем сохранённый шрифт — ДО рендера UI
  applyFont(getFont());
  buildSwitcher();
}

// Запускаем как можно раньше чтобы не было FOUC
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

export { applyFont, getFont, FONTS };