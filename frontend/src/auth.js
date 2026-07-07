/* =====================================================================
 *  Вариант B — логика модального окна авторизации / регистрации
 * ===================================================================== */

(function () {
  "use strict";

  const USERS_KEY = "witcherAcademyUsers";
  const CURRENT_USER_KEY = "witcherAcademyLoggedInUser";
  const POST_AUTH_INTENT_KEY = "witcherAcademyPostAuthIntent";

  const state = {
    mode: "login",
    authOpen: false,
    warningOpen: false,
    error: "",
    notice: "",
  };

  function byId(id) {
    return document.getElementById(id);
  }

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

  function redirectToCabinet() {
    window.location.href = "cabinet.html";
  }

  function setMessage(node, text) {
    if (!node) return;
    node.textContent = text || "";
    node.hidden = !text;
  }

  function lockScroll(locked) {
    document.body.style.overflow = locked ? "hidden" : "";
  }

  function syncScrollLock() {
    lockScroll(state.authOpen || state.warningOpen);
  }

  function updateAuthButtons() {
    const user = getCurrentUser();
    const label = user ? "Кабинет · " + user.username : "Авторизация";

    const authButtons = [byId("authActionBtn"), byId("mobileAuthAction")];
    const logoutButtons = [byId("authLogoutBtn"), byId("mobileLogoutAction")];

    authButtons.forEach(function (btn) {
      if (!btn) return;
      btn.textContent = label;
      btn.classList.remove("is-hidden");
    });

    logoutButtons.forEach(function (btn) {
      if (!btn) return;
      if (user) btn.classList.remove("is-hidden");
      else btn.classList.add("is-hidden");
    });
  }

  function applyAuthMode() {
    const isLogin = state.mode === "login";
    const title = byId("authModalTitle");
    const submit = byId("authSubmitButton");
    const toggle = byId("authToggleMode");

    if (title) title.textContent = isLogin ? "Авторизация" : "Регистрация";
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
    setMessage(byId("authErrorBox"), state.error);
  }

  function openAuthModal(mode, notice) {
    state.mode = mode || "login";
    state.authOpen = true;
    state.error = "";
    state.notice = notice || "";

    const modal = byId("authModalBackdrop");
    if (modal) {
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
    }

    closeWarningModal();
    renderAuthState();
    syncScrollLock();

    const username = byId("authUsername");
    if (username) {
      window.setTimeout(function () {
        username.focus();
      }, 40);
    }
  }

  function closeAuthModal() {
    state.authOpen = false;
    state.error = "";
    state.notice = "";

    const modal = byId("authModalBackdrop");
    if (modal) {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
    }

    syncScrollLock();
  }

  function openWarningModal() {
    state.warningOpen = true;
    const modal = byId("authWarningBackdrop");
    if (modal) {
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
    }
    syncScrollLock();
  }

  function closeWarningModal() {
    state.warningOpen = false;
    const modal = byId("authWarningBackdrop");
    if (modal) {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
    }
    syncScrollLock();
  }

  function handleAuthSubmit(event) {
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

    if (state.mode === "login") {
      const user = users[username];
      if (!user || user.password !== password) {
        state.error = "Неверное имя пользователя или пароль.";
        renderAuthState();
        return;
      }

      setCurrentUser({
        username: username,
        registeredAt: user.registeredAt,
        loginAt: new Date().toISOString(),
      });

      updateAuthButtons();
      closeAuthModal();
      redirectToCabinet();
      return;
    }

    if (users[username]) {
      state.error = "Имя пользователя уже занято.";
      renderAuthState();
      return;
    }

    users[username] = {
      password: password,
      registeredAt: new Date().toISOString(),
    };
    writeUsers(users);

    state.mode = "login";
    state.error = "";
    state.notice = "Регистрация успешна. Теперь войдите в систему.";

    const form = byId("authForm");
    if (form) form.reset();
    renderAuthState();
  }

  function bindAuthModal() {
    const modal = byId("authModalBackdrop");
    const closeBtn = byId("authModalCloseBtn");
    const toggleBtn = byId("authToggleMode");
    const form = byId("authForm");

    modal?.addEventListener("click", function (event) {
      if (event.target === modal) closeAuthModal();
    });

    closeBtn?.addEventListener("click", closeAuthModal);

    toggleBtn?.addEventListener("click", function () {
      state.mode = state.mode === "login" ? "register" : "login";
      state.error = "";
      state.notice = "";
      renderAuthState();
    });

    form?.addEventListener("submit", handleAuthSubmit);
  }

  function bindWarningModal() {
    const modal = byId("authWarningBackdrop");
    const cancelBtn = byId("authWarningCancelBtn");
    const continueBtn = byId("authWarningContinueBtn");

    modal?.addEventListener("click", function (event) {
      if (event.target === modal) closeWarningModal();
    });

    cancelBtn?.addEventListener("click", closeWarningModal);

    continueBtn?.addEventListener("click", function () {
      localStorage.setItem(POST_AUTH_INTENT_KEY, "create-contract");
      const mode = hasRegisteredUsers() ? "login" : "register";
      const notice = hasRegisteredUsers()
        ? "Авторизуйтесь, чтобы получить доступ к размещению контрактов."
        : "Сначала зарегистрируйтесь, чтобы получить доступ к размещению контрактов.";
      openAuthModal(mode, notice);
    });
  }

  function bindHeaderButtons() {
    const authButtons = [byId("authActionBtn"), byId("mobileAuthAction")];
    const logoutButtons = [byId("authLogoutBtn"), byId("mobileLogoutAction")];

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

  function bindEsc() {
    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape") return;
      if (state.authOpen) {
        closeAuthModal();
        return;
      }
      if (state.warningOpen) closeWarningModal();
    });
  }

  function init() {
    updateAuthButtons();
    bindHeaderButtons();
    bindAuthModal();
    bindWarningModal();
    bindEsc();
    renderAuthState();
  }

  window.WitcherAuth = {
    isLoggedIn: isLoggedIn,
    getCurrentUser: getCurrentUser,
    logout: logout,
    openAuthModal: openAuthModal,
    openAuthRequiredWarning: openWarningModal,
    updateAuthButtons: updateAuthButtons,
    redirectToCabinet: redirectToCabinet,
    postAuthIntentKey: POST_AUTH_INTENT_KEY,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
