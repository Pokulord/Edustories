/* =====================================================================
 *  auth.js — логика авторизации / регистрации (нативный <dialog>)
 * ===================================================================== */

(function () {
  "use strict";

  const USERS_KEY           = "witcherAcademyUsers";
  const CURRENT_USER_KEY    = "witcherAcademyLoggedInUser";
  const POST_AUTH_INTENT_KEY = "witcherAcademyPostAuthIntent";

  const state = {
    mode: "login",
    error: "",
    notice: "",
  };

  /* ─── utils ─────────────────────────────────────────────────────── */

  function byId(id) {
    return document.getElementById(id);
  }

  /* ─── storage ────────────────────────────────────────────────────── */

  function readUsers() {
    try {
      const raw = localStorage.getItem(USERS_KEY);
      if (!raw) return {};
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" ? parsed : {};
    } catch (_) {
      return {};
    }
  }

  function writeUsers(users) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
  }

  function hasRegisteredUsers() {
    return Object.keys(readUsers()).length > 0;
  }

  function getCurrentUser() {
    try {
      const raw = localStorage.getItem(CURRENT_USER_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed.username === "string" ? parsed : null;
    } catch (_) {
      return null;
    }
  }

  function setCurrentUser(user) {
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
  }

  function isLoggedIn() {
    return Boolean(getCurrentUser());
  }

  function logout() {
    localStorage.removeItem(CURRENT_USER_KEY);
    localStorage.removeItem(POST_AUTH_INTENT_KEY);
    updateAuthButtons();
  }

  /* ─── navigation ─────────────────────────────────────────────────── */

  function redirectToCabinet() {
    window.location.href = "cabinet.html";
  }

  /* ─── ui helpers ─────────────────────────────────────────────────── */

  function setMessage(node, text) {
    if (!node) return;
    node.textContent = text || "";
    node.hidden = !text;
  }

  /* ─── auth buttons ───────────────────────────────────────────────── */

  function updateAuthButtons() {
    const user  = getCurrentUser();
    const label = user ? "Кабинет · " + user.username : "Авторизация";

    [byId("authActionBtn"), byId("mobileAuthAction")].forEach(function (btn) {
      if (!btn) return;
      btn.textContent = label;
      btn.classList.remove("is-hidden");
    });

    [byId("authLogoutBtn"), byId("mobileLogoutAction")].forEach(function (btn) {
      if (!btn) return;
      if (user) btn.classList.remove("is-hidden");
      else       btn.classList.add("is-hidden");
    });
  }

  /* ─── auth modal render ──────────────────────────────────────────── */

  function applyAuthMode() {
    const isLogin = state.mode === "login";

    const title  = byId("authModalTitle");
    const submit = byId("authSubmitButton");
    const toggle = byId("authToggleMode");

    if (title)  title.textContent  = isLogin ? "Авторизация" : "Регистрация";
    if (submit) submit.textContent = isLogin ? "Войти" : "Зарегистрироваться";
    if (toggle) {
      toggle.textContent = isLogin
        ? "Нет аккаунта? Зарегистрироваться"
        : "Уже есть аккаунт? Войти";
    }
  }

  function renderAuthState() {
    applyAuthMode();
    setMessage(byId("authNoticeBox"), state.notice);
    setMessage(byId("authErrorBox"),  state.error);
  }

  /* ─── dialog open / close ────────────────────────────────────────── */

  /**
   * Открыть auth modal.
   * Используем нативный showModal() — браузер сам блокирует скролл
   * и добавляет inert на остальной контент.
   */
  function openAuthModal(mode, notice) {
    state.mode   = mode   || "login";
    state.error  = "";
    state.notice = notice || "";

    renderAuthState();

    const modal = byId("authModal");
    if (!modal) return;

    // Закрываем warning, если был открыт
    const warning = byId("authWarningModal");
    if (warning && warning.open) warning.close();

    // showModal() бросит исключение, если уже открыт
    if (!modal.open) modal.showModal();

    // Фокус на поле ввода
    const username = byId("authUsername");
    if (username) {
      window.setTimeout(function () { username.focus(); }, 40);
    }
  }

  function closeAuthModal() {
    state.error  = "";
    state.notice = "";

    const modal = byId("authModal");
    if (modal && modal.open) modal.close();
  }

  function openWarningModal() {
    const modal = byId("authWarningModal");
    if (modal && !modal.open) modal.showModal();
  }

  function closeWarningModal() {
    const modal = byId("authWarningModal");
    if (modal && modal.open) modal.close();
  }

  /* ─── backdrop click helper ──────────────────────────────────────── */

  /**
   * Нативный <dialog> не закрывается по клику на ::backdrop автоматически.
   * Определяем клик по бэкдропу через getBoundingClientRect:
   * если клик вышел за пределы диалога — закрываем.
   */
  function bindBackdropClose(dialogEl, closeFn) {
    if (!dialogEl) return;

    dialogEl.addEventListener("click", function (e) {
      const rect = dialogEl.getBoundingClientRect();
      const clickedInside =
        e.clientX >= rect.left &&
        e.clientX <= rect.right &&
        e.clientY >= rect.top  &&
        e.clientY <= rect.bottom;

      if (!clickedInside) closeFn();
    });
  }

  /* ─── form submit ────────────────────────────────────────────────── */

  function handleAuthSubmit(event) {
    // Предотвращаем нативное закрытие dialog от method="dialog"
    event.preventDefault();

    const usernameInput = byId("authUsername");
    const passwordInput = byId("authPassword");
    const username = usernameInput ? usernameInput.value.trim() : "";
    const password = passwordInput ? passwordInput.value : "";

    if (username.length < 3) {
      state.error = "Имя пользователя должно содержать не менее 3 символов.";
      renderAuthState();
      return;
    }

    if (password.length < 4) {
      state.error = "Пароль должен содержать не менее 4 символов.";
      renderAuthState();
      return;
    }

    const users = readUsers();

    /* ── login ── */
    if (state.mode === "login") {
      const user = users[username];

      if (!user || user.password !== password) {
        state.error = "Неверное имя пользователя или пароль.";
        renderAuthState();
        return;
      }

      setCurrentUser({
        username:     username,
        registeredAt: user.registeredAt,
        loginAt:      new Date().toISOString(),
      });

      updateAuthButtons();
      closeAuthModal();
      redirectToCabinet();
      return;
    }

    /* ── register ── */
    if (users[username]) {
      state.error = "Имя пользователя уже занято.";
      renderAuthState();
      return;
    }

    users[username] = {
      password:     password,
      registeredAt: new Date().toISOString(),
    };
    writeUsers(users);

    state.mode   = "login";
    state.error  = "";
    state.notice = "Регистрация успешна. Теперь войдите в систему.";

    const form = byId("authForm");
    if (form) form.reset();

    renderAuthState();
  }

  /* ─── bind: auth modal ───────────────────────────────────────────── */

  function bindAuthModal() {
    const modal     = byId("authModal");
    const closeBtn  = byId("authModalCloseBtn");
    const toggleBtn = byId("authToggleMode");
    const form      = byId("authForm");

    // Закрытие по backdrop
    bindBackdropClose(modal, closeAuthModal);

    // Кнопка X
    closeBtn?.addEventListener("click", closeAuthModal);

    // Переключение login ↔ register
    toggleBtn?.addEventListener("click", function () {
      state.mode   = state.mode === "login" ? "register" : "login";
      state.error  = "";
      state.notice = "";
      renderAuthState();
    });

    // Отправка формы
    form?.addEventListener("submit", handleAuthSubmit);

    // Нативное событие закрытия (Esc браузером или dialog.close())
    // Синхронизируем state, чтобы не было рассинхрона
    modal?.addEventListener("close", function () {
      state.error  = "";
      state.notice = "";
    });
  }

  /* ─── bind: warning modal ────────────────────────────────────────── */

  function bindWarningModal() {
    const modal       = byId("authWarningModal");
    const cancelBtn   = byId("authWarningCancelBtn");
    const continueBtn = byId("authWarningContinueBtn");

    bindBackdropClose(modal, closeWarningModal);

    cancelBtn?.addEventListener("click", closeWarningModal);

    continueBtn?.addEventListener("click", function () {
      localStorage.setItem(POST_AUTH_INTENT_KEY, "create-contract");

      const mode = hasRegisteredUsers() ? "login" : "register";
      const notice = hasRegisteredUsers()
        ? "Авторизуйтесь, чтобы получить доступ к размещению контрактов."
        : "Сначала зарегистрируйтесь, чтобы получить доступ к размещению контрактов.";

      openAuthModal(mode, notice);
    });

    modal?.addEventListener("close", function () {
      // ничего не нужно, state не хранит warningOpen
    });
  }

  /* ─── bind: header buttons ───────────────────────────────────────── */

  function bindHeaderButtons() {
    const authButtons   = [byId("authActionBtn"),  byId("mobileAuthAction")];
    const logoutButtons = [byId("authLogoutBtn"),   byId("mobileLogoutAction")];

    function onAuthClick(event) {
      event.preventDefault();

      if (isLoggedIn()) {
        redirectToCabinet();
        return;
      }

      const mode = hasRegisteredUsers() ? "login" : "register";
      const notice = hasRegisteredUsers()
        ? "Войдите в систему Академии Ведьмаков."
        : "У вас ещё нет аккаунта. Сначала создайте его в Академии Ведьмаков.";

      openAuthModal(mode, notice);
    }

    function onLogoutClick(event) {
      event.preventDefault();
      logout();
      alert("Вы вышли из аккаунта.");
      window.location.href = "/";
    }

    authButtons.forEach(function (btn) {
      btn?.addEventListener("click", onAuthClick);
    });

    logoutButtons.forEach(function (btn) {
      btn?.addEventListener("click", onLogoutClick);
    });
  }

  /* ─── bind: Escape ───────────────────────────────────────────────── */

  /**
   * Нативный <dialog> уже закрывается по Escape самостоятельно.
   * Дополнительно слушаем только если нужна кастомная логика.
   * Здесь — просто оставляем браузерное поведение (ничего не делаем).
   */
  function bindEsc() {
    // Нативный Escape обрабатывается браузером автоматически.
    // Событие "close" на dialog отловит закрытие и очистит state.
    // Дополнительный keydown не нужен.
  }

  /* ─── init ───────────────────────────────────────────────────────── */

  function init() {
    updateAuthButtons();
    bindHeaderButtons();
    bindAuthModal();
    bindWarningModal();
    bindEsc();
    renderAuthState();
  }

  /* ─── public API ─────────────────────────────────────────────────── */

  window.WitcherAuth = {
    isLoggedIn:              isLoggedIn,
    getCurrentUser:          getCurrentUser,
    logout:                  logout,
    openAuthModal:           openAuthModal,
    openAuthRequiredWarning: openWarningModal,
    updateAuthButtons:       updateAuthButtons,
    redirectToCabinet:       redirectToCabinet,
    postAuthIntentKey:       POST_AUTH_INTENT_KEY,
  };

  /* ─── bootstrap ──────────────────────────────────────────────────── */

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();