(function () {
  "use strict";

  function el(html) {
    const tmp = document.createElement("template");
    tmp.innerHTML = html.trim();
    return tmp.content.firstElementChild;
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function pluralizeContracts(n) {
    const mod10 = n % 10;
    const mod100 = n % 100;
    if (mod10 === 1 && mod100 !== 11) return "контракт";
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
      return "контракта";
    }
    return "контрактов";
  }

  function formatDate(iso) {
    if (!iso) return "";
    try {
      return new Date(iso).toLocaleString("ru-RU", {
        day: "2-digit",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (_) {
      return iso;
    }
  }

  function modalRoot() {
    return document.getElementById("modalRoot");
  }

  function lockScroll(lock) {
    document.body.style.overflow = lock ? "hidden" : "";
  }

  function emptyForm() {
    return {
      fullName: "",
      groupAndDiscipline: "",
      subject: "",
      taskType: "",
      topic: "",
      deadline: "",
      contactMethod: "",
      additionalRequirements: "",
    };
  }

  const TASK_TYPES = [
    "Курсовая работа",
    "РГР (расчётно-графическая)",
    "Лабораторная работа",
    "Контрольная работа",
    "Реферат",
    "Дипломная работа",
    "Эссе",
    "Решение задач",
    "Другое",
  ];

  const DEMO_CONTRACTS = [
    {
      id: 1001,
      fullName: "Геральт из Ривии",
      groupAndDiscipline: "ИКБО-12-21 / Дисциплина №3",
      subject: "Знаки и Заклинания",
      taskType: "Курсовая работа",
      topic: "Боевые знаки ведьмака: Аард, Игни, Аксий, Ирден, Квен",
      deadline: "до 25.12.2026",
      contactMethod: "@white_wolf",
      additionalRequirements: "Оформление по ГОСТ, обязательны схемы и иллюстрации знаков. Антиплагиат не ниже 70%.",
      createdAt: new Date().toISOString(),
      _demo: true,
    },
    {
      id: 1002,
      fullName: "Йеннифэр из Венгерберга",
      groupAndDiscipline: "АЛХМ-04-23 / Дисциплина №7",
      subject: "Бестиарий Севера",
      taskType: "Реферат",
      topic: "Чудовища Континента: классификация и слабости",
      deadline: "7 дней",
      contactMethod: "yennefer@vengerberg.kaedwen",
      additionalRequirements: "Минимум 5 источников, обязательны иллюстрации.",
      createdAt: new Date().toISOString(),
      _demo: true,
    },
    {
      id: 1003,
      fullName: "Лютик",
      groupAndDiscipline: "АЛХМ-04-23 / Дисциплина №2",
      subject: "Алхимия Зелий и Бомб",
      taskType: "Лабораторная работа",
      topic: "Приготовление эликсира «Ласточка»",
      deadline: "до 12.04.2026",
      contactMethod: "вк: dandelion_bard",
      additionalRequirements: "",
      createdAt: new Date().toISOString(),
      _demo: true,
    },
  ];

  const state = {
    contracts: [],
    activeContract: null,
    formOpen: false,
    formStep: 1,
    form: emptyForm(),
    submitting: false,
    formError: null,
  };

  const STORAGE_KEY = "contracts_stub";

  function readStoredContracts() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (_) {
      return [];
    }
  }

  function saveStoredContracts(contracts) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(contracts));
  }

  function spawnFireflies() {
    const host = document.getElementById("fireflies");
    if (!host) return;
    const COUNT = 25;
    for (let i = 0; i < COUNT; i++) {
      const firefly = document.createElement("span");
      firefly.className = "firefly";
      firefly.style.left = Math.random() * 100 + "%";
      firefly.style.bottom = "-10px";
      firefly.style.transform = "scale(" + (0.5 + Math.random() * 1.2).toFixed(2) + ")";
      firefly.style.animationDuration = (8 + Math.random() * 10) + "s, " + (1 + Math.random() * 2) + "s";
      firefly.style.animationDelay = (-Math.random() * 8) + "s, " + (-Math.random() * 2) + "s";
      host.appendChild(firefly);
    }
  }

  function initBurger() {
    const btn = document.getElementById("burger");
    const menu = document.getElementById("mobileMenu");
    if (!btn || !menu) return;

    btn.addEventListener("click", function () {
      menu.classList.toggle("is-open");
    });

    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        menu.classList.remove("is-open");
      });
    });
  }

  function renderContracts() {
    const grid = document.getElementById("contractsGrid");
    const countLabel = document.getElementById("contractsCountLabel");
    const heroStat = document.getElementById("statContractCount");
    if (!grid) return;

    grid.innerHTML = "";

    if (state.contracts.length === 0) {
      grid.appendChild(
        el(
          '<div class="md:col-span-2 xl:col-span-3 bg-[#0b1f1c] border border-emerald-900/40 rounded-xl p-12 text-center">' +
            '<h3 class="text-xl text-emerald-200 mb-3">Доска контрактов пуста</h3>' +
            '<p class="text-emerald-200/60 text-sm mb-6">Будь первым, кто разместит контракт. Гильдия ждёт.</p>' +
            '<button data-action="open-form" class="px-6 py-2.5 bg-gradient-to-r from-amber-700 to-amber-500 text-black font-semibold rounded-md text-sm uppercase tracking-widest hover:scale-105 transition">Разместить Контракт</button>' +
          '</div>'
        )
      );
    } else {
      state.contracts.forEach(function (contract) {
        grid.appendChild(buildContractCard(contract));
      });
    }

    if (countLabel) {
      countLabel.textContent = state.contracts.length + " " + pluralizeContracts(state.contracts.length) + " доступно";
    }

    if (heroStat) {
      heroStat.textContent = String(state.contracts.length);
    }
  }

  function buildContractCard(contract) {
    const sideBadge = contract._demo
      ? '<span class="text-[10px] uppercase tracking-widest text-emerald-400/50">пример</span>'
      : '<span class="text-[10px] uppercase tracking-widest text-emerald-400/50">№ ' + String(contract.id).padStart(4, "0") + '</span>';

    return el(
      '<div class="group bg-[#0b1f1c] border border-emerald-900/40 rounded-xl overflow-hidden hover:border-emerald-400/50 transition duration-500 shadow-[0_0_25px_rgba(0,0,0,0.6)] flex flex-col">' +
        '<div class="h-40 bg-cover bg-center opacity-80" style="background-image:url(\'/images/wedya.jpg\')"></div>' +
        '<div class="p-6 flex flex-col flex-1">' +
          '<div class="flex items-center justify-between mb-3">' +
            '<span class="inline-block px-3 py-1 rounded-full text-[11px] uppercase tracking-widest text-amber-300 border border-amber-500/40 bg-amber-500/10">' + escapeHtml(contract.taskType) + '</span>' +
            sideBadge +
          '</div>' +
          '<h3 class="text-lg text-emerald-200 mb-3 leading-snug">' + escapeHtml(contract.subject) + '</h3>' +
          '<div class="space-y-2 text-sm text-emerald-200/70 mb-6">' +
            '<div class="flex gap-2"><span class="text-emerald-400/60 text-[11px] uppercase tracking-widest w-16 shrink-0 pt-0.5">Тема</span><span class="line-clamp-2">' + escapeHtml(contract.topic) + '</span></div>' +
            '<div class="flex gap-2"><span class="text-emerald-400/60 text-[11px] uppercase tracking-widest w-16 shrink-0 pt-0.5">Срок</span><span class="text-amber-300/90">' + escapeHtml(contract.deadline) + '</span></div>' +
          '</div>' +
          '<button data-action="open-details" data-id="' + contract.id + '" class="mt-auto w-full py-2 border border-emerald-400/50 text-emerald-200 rounded-md hover:bg-emerald-400/10 transition duration-300 text-sm">Изучить Контракт</button>' +
        '</div>' +
      '</div>'
    );
  }

  async function loadContracts() {
    const stored = readStoredContracts();
    state.contracts = stored.length ? stored : DEMO_CONTRACTS.slice();
    renderContracts();
  }

  function step1Valid() {
    const f = state.form;
    return f.fullName.trim() && f.groupAndDiscipline.trim() && f.subject.trim() && f.taskType.trim();
  }

  function step2Valid() {
    const f = state.form;
    return f.topic.trim() && f.deadline.trim() && f.contactMethod.trim();
  }

  function openForm() {
    state.formOpen = true;
    state.formStep = 1;
    state.form = emptyForm();
    state.formError = null;
    state.submitting = false;
    renderForm();
    lockScroll(true);
  }

  function closeForm() {
    state.formOpen = false;
    const root = modalRoot();
    if (root) {
      const modal = root.querySelector('[data-modal="form"]');
      if (modal) modal.remove();
    }
    if (!state.activeContract) lockScroll(false);
  }

  function formField(label, required, control) {
    return '<label class="block">' +
      '<span class="block text-sm tracking-wide text-emerald-300 mb-1.5">' +
        escapeHtml(label) + (required ? ' <span class="text-amber-400">*</span>' : '') +
      '</span>' +
      control +
    '</label>';
  }

  function renderForm() {
    const root = modalRoot();
    if (!root) return;

    const oldModal = root.querySelector('[data-modal="form"]');
    if (oldModal) oldModal.remove();
    if (!state.formOpen) return;

    const form = state.form;
    const step = state.formStep;

    const taskOptions = TASK_TYPES.map(function (type) {
      const selected = type === form.taskType ? ' selected' : '';
      return '<option value="' + escapeHtml(type) + '"' + selected + '>' + escapeHtml(type) + '</option>';
    }).join('');

    const step1 =
      '<div class="space-y-4">' +
        formField('ФИО', true,
          '<input data-field="fullName" type="text" class="input-mystic" placeholder="Иванов Иван Иванович" value="' + escapeHtml(form.fullName) + '">') +
        formField('Группа и номер дисциплины', true,
          '<input data-field="groupAndDiscipline" type="text" class="input-mystic" placeholder="ИКБО-12-21 / Дисциплина №3" value="' + escapeHtml(form.groupAndDiscipline) + '">') +
        formField('Предмет', true,
          '<input data-field="subject" type="text" class="input-mystic" placeholder="Высшая математика" value="' + escapeHtml(form.subject) + '">') +
        formField('Задание (тип работы)', true,
          '<select data-field="taskType" class="input-mystic"><option value="">— Выберите тип работы —</option>' + taskOptions + '</select>') +
      '</div>';

    const step2 =
      '<div class="space-y-4">' +
        formField('Тема', true,
          '<input data-field="topic" type="text" class="input-mystic" placeholder="Например: Численные методы решения СЛАУ" value="' + escapeHtml(form.topic) + '">') +
        formField('Сроки выполнения работы', true,
          '<input data-field="deadline" type="text" class="input-mystic" placeholder="до 25.12.2026 или 7 дней" value="' + escapeHtml(form.deadline) + '">') +
        formField('Способ связи (почта, ник Telegram или ВК)', true,
          '<input data-field="contactMethod" type="text" class="input-mystic" placeholder="@witcher_geralt или mail@example.com" value="' + escapeHtml(form.contactMethod) + '">') +
        formField('Дополнительные требования', false,
          '<textarea data-field="additionalRequirements" rows="4" class="input-mystic" placeholder="Оформление по ГОСТ, обязательны графики, антиплагиат от 70%...">' + escapeHtml(form.additionalRequirements) + '</textarea>') +
      '</div>';

    const errorBlock = state.formError
      ? '<div class="mt-4 rounded-md border border-red-500/40 bg-red-900/20 px-3 py-2 text-sm text-red-300">' + escapeHtml(state.formError) + '</div>'
      : '';

    const leftButton = step === 1
      ? '<button data-action="cancel" type="button" class="px-5 py-2.5 border border-emerald-400/50 text-emerald-200 rounded-md hover:bg-emerald-400/10 transition">Отмена</button>'
      : '<button data-action="back" type="button" class="px-5 py-2.5 border border-emerald-400/50 text-emerald-200 rounded-md hover:bg-emerald-400/10 transition">← Назад</button>';

    const rightButton = step === 1
      ? '<button data-action="next" type="button"' + (step1Valid() ? '' : ' disabled') + ' class="px-6 py-2.5 bg-gradient-to-r from-amber-700 to-amber-500 text-black font-semibold rounded-md shadow-[0_0_15px_rgba(251,191,36,0.4)] hover:shadow-[0_0_30px_rgba(251,191,36,0.7)] transition disabled:opacity-50 disabled:cursor-not-allowed">Далее →</button>'
      : '<button data-action="submit" type="submit"' + (state.submitting || !step2Valid() ? ' disabled' : '') + ' class="px-6 py-2.5 bg-gradient-to-r from-amber-700 to-amber-500 text-black font-semibold rounded-md shadow-[0_0_15px_rgba(251,191,36,0.4)] hover:shadow-[0_0_30px_rgba(251,191,36,0.7)] transition disabled:opacity-50 disabled:cursor-not-allowed">' + (state.submitting ? 'Запечатываем свиток...' : 'Разместить контракт') + '</button>';

    const modal = el(
      '<div data-modal="form" class="modal-backdrop fixed inset-0 z-[100] flex items-center justify-center p-4 overflow-y-auto" style="background:rgba(2,8,7,0.78);backdrop-filter:blur(4px)">' +
        '<div data-stop class="modal-panel relative w-full max-w-2xl bg-[#0b1f1c] border border-emerald-900/60 rounded-xl shadow-[0_0_50px_rgba(0,0,0,0.7)] my-8">' +
          '<div class="flex items-start justify-between border-b border-emerald-900/60 p-6">' +
            '<div>' +
              '<div class="text-[10px] uppercase tracking-[0.3em] text-emerald-400/60">Этап ' + step + ' / 2</div>' +
              '<h2 class="text-2xl text-emerald-200 mt-1 font-semibold drop-shadow-[0_0_15px_rgba(16,185,129,0.35)]">' + (step === 1 ? 'Новый Контракт · Заказчик' : 'Новый Контракт · Задание') + '</h2>' +
            '</div>' +
            '<button data-action="close" type="button" class="text-emerald-300/60 hover:text-emerald-300 transition" aria-label="Закрыть">' +
              '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M6 18L18 6"/></svg>' +
            '</button>' +
          '</div>' +
          '<div class="px-6 pt-4 flex gap-2">' +
            '<div class="h-1 flex-1 rounded-full" style="background:linear-gradient(90deg,#10b981 0%,#34d399 100%);box-shadow:0 0 12px rgba(16,185,129,0.5)"></div>' +
            '<div class="h-1 flex-1 rounded-full" style="' + (step === 2 ? 'background:linear-gradient(90deg,#10b981 0%,#34d399 100%);box-shadow:0 0 12px rgba(16,185,129,0.5)' : 'background:rgba(16,185,129,0.18)') + '"></div>' +
          '</div>' +
          '<form data-form class="p-6">' +
            (step === 1 ? step1 : step2) +
            errorBlock +
            '<div class="mt-6 flex items-center justify-between gap-3">' + leftButton + rightButton + '</div>' +
          '</form>' +
        '</div>' +
      '</div>'
    );

    root.appendChild(modal);
    wireForm(modal);
  }

  function wireForm(modal) {
    modal.addEventListener('click', function (event) {
      if (!event.target.closest('[data-stop]')) closeForm();
    });

    modal.querySelectorAll('[data-action="close"], [data-action="cancel"]').forEach(function (button) {
      button.addEventListener('click', closeForm);
    });

    modal.querySelectorAll('[data-field]').forEach(function (input) {
      const field = input.getAttribute('data-field');
      input.addEventListener('input', function () {
        state.form[field] = input.value;
        const next = modal.querySelector('[data-action="next"]');
        const submit = modal.querySelector('[data-action="submit"]');
        if (next) next.disabled = !step1Valid();
        if (submit) submit.disabled = state.submitting || !step2Valid();
      });
    });

    const nextButton = modal.querySelector('[data-action="next"]');
    if (nextButton) {
      nextButton.addEventListener('click', function () {
        if (!step1Valid()) {
          state.formError = 'Заполните все обязательные поля первого этапа';
          renderForm();
          return;
        }
        state.formError = null;
        state.formStep = 2;
        renderForm();
      });
    }

    const backButton = modal.querySelector('[data-action="back"]');
    if (backButton) {
      backButton.addEventListener('click', function () {
        state.formError = null;
        state.formStep = 1;
        renderForm();
      });
    }

    const form = modal.querySelector('[data-form]');
    if (!form) return;

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      if (!step2Valid()) {
        state.formError = 'Заполните обязательные поля';
        renderForm();
        return;
      }

      state.submitting = true;
      state.formError = null;
      renderForm();

      try {
        const newContract = {
          id: Date.now(),
          fullName: state.form.fullName,
          groupAndDiscipline: state.form.groupAndDiscipline,
          subject: state.form.subject,
          taskType: state.form.taskType,
          topic: state.form.topic,
          deadline: state.form.deadline,
          contactMethod: state.form.contactMethod,
          additionalRequirements: state.form.additionalRequirements,
          createdAt: new Date().toISOString(),
        };

        const hasOnlyDemo = state.contracts.every(function (item) { return item._demo; });
        state.contracts = hasOnlyDemo ? [newContract] : [newContract].concat(state.contracts);
        saveStoredContracts(state.contracts);
        renderContracts();
        closeForm();
      } catch (error) {
        state.submitting = false;
        state.formError = error && error.message ? error.message : 'Ошибка отправки';
        renderForm();
      }
    });
  }

  function openDetails(id) {
    const contract = state.contracts.find(function (item) {
      return String(item.id) === String(id);
    });
    if (!contract) return;
    state.activeContract = contract;
    renderDetails();
    lockScroll(true);
  }

  function closeDetails() {
    state.activeContract = null;
    const root = modalRoot();
    if (root) {
      const modal = root.querySelector('[data-modal="details"]');
      if (modal) modal.remove();
    }
    if (!state.formOpen) lockScroll(false);
  }

  function detailRow(label, value, options) {
    const opts = options || {};
    const classes = [];
    classes.push(opts.accent === 'gold' ? 'text-amber-300' : 'text-emerald-100');
    if (opts.mono) classes.push('font-mono', 'text-sm');
    if (opts.multiline) classes.push('whitespace-pre-wrap');

    return '<div>' +
      '<div class="mb-1 text-[10px] uppercase tracking-[0.2em] text-emerald-400/60">' + escapeHtml(label) + '</div>' +
      '<div class="' + classes.join(' ') + '">' + escapeHtml(value) + '</div>' +
    '</div>';
  }

  function renderDetails() {
    const root = modalRoot();
    if (!root || !state.activeContract) return;

    const oldModal = root.querySelector('[data-modal="details"]');
    if (oldModal) oldModal.remove();

    const contract = state.activeContract;
    const modal = el(
      '<div data-modal="details" class="modal-backdrop fixed inset-0 z-[100] flex items-center justify-center p-4 overflow-y-auto" style="background:rgba(2,8,7,0.78);backdrop-filter:blur(4px)">' +
        '<div data-stop class="modal-panel relative w-full max-w-2xl bg-[#0b1f1c] border border-emerald-900/60 rounded-xl shadow-[0_0_50px_rgba(0,0,0,0.7)] my-8">' +
          '<div class="flex items-start justify-between border-b border-emerald-900/60 p-6">' +
            '<div>' +
              '<div class="text-[10px] uppercase tracking-[0.3em] text-emerald-400/60">Контракт № ' + String(contract.id).padStart(4, '0') + ' · ' + escapeHtml(formatDate(contract.createdAt)) + '</div>' +
              '<h2 class="text-2xl text-emerald-200 mt-1 font-semibold drop-shadow-[0_0_15px_rgba(16,185,129,0.35)]">' + escapeHtml(contract.subject) + '</h2>' +
              '<div class="mt-2"><span class="inline-block px-3 py-1 rounded-full text-[11px] uppercase tracking-widest text-amber-300 border border-amber-500/40 bg-amber-500/10">' + escapeHtml(contract.taskType) + '</span></div>' +
            '</div>' +
            '<button data-action="close" type="button" class="text-emerald-300/60 hover:text-emerald-300 transition" aria-label="Закрыть">' +
              '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M6 18L18 6"/></svg>' +
            '</button>' +
          '</div>' +
          '<div class="p-6 space-y-5">' +
            detailRow('ФИО заказчика', contract.fullName) +
            detailRow('Группа и номер дисциплины', contract.groupAndDiscipline) +
            detailRow('Тема', contract.topic) +
            detailRow('Сроки выполнения', contract.deadline, { accent: 'gold' }) +
            detailRow('Способ связи', contract.contactMethod, { mono: true }) +
            detailRow('Дополнительные требования', contract.additionalRequirements || '— не указано —', { multiline: true }) +
          '</div>' +
          '<div class="border-t border-emerald-900/60 p-6">' +
            '<button data-action="close" type="button" class="w-full py-3 bg-gradient-to-r from-amber-700 to-amber-500 text-black font-semibold rounded-md shadow-[0_0_25px_rgba(251,191,36,0.4)] hover:shadow-[0_0_45px_rgba(251,191,36,0.7)] transition tracking-widest uppercase text-sm">Взять Контракт в Работу</button>' +
            '<p class="text-center text-xs text-emerald-400/60 mt-3">Свяжитесь с заказчиком указанным способом, чтобы обсудить детали.</p>' +
          '</div>' +
        '</div>' +
      '</div>'
    );

    root.appendChild(modal);

    modal.addEventListener('click', function (event) {
      if (!event.target.closest('[data-stop]')) closeDetails();
    });

    modal.querySelectorAll('[data-action="close"]').forEach(function (button) {
      button.addEventListener('click', closeDetails);
    });
  }

  function initGlobalActions() {
    document.addEventListener('click', function (event) {
      const openFormBtn = event.target.closest('[data-action="open-form"], #openContractFormBtn');
      if (openFormBtn) {
        event.preventDefault();
        openForm();
        return;
      }

      const openDetailsBtn = event.target.closest('[data-action="open-details"]');
      if (openDetailsBtn) {
        event.preventDefault();
        openDetails(openDetailsBtn.getAttribute('data-id'));
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape') return;
      if (state.activeContract) closeDetails();
      else if (state.formOpen) closeForm();
    });
  }

  function init() {
    spawnFireflies();
    initBurger();
    initGlobalActions();
    loadContracts();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();