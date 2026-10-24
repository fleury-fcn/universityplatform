/* ISTA — comportements communs : thème, hors ligne, confirmations, service worker. */
(function () {
  "use strict";

  var root = document.documentElement;

  function storedTheme() {
    try { return localStorage.getItem("theme"); } catch (e) { return null; }
  }

  function effectiveTheme() {
    var t = storedTheme();
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = effectiveTheme() === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) { /* stockage indisponible */ }
    });
  });

  // Bandeau hors ligne
  var banner = document.querySelector("[data-offline-banner]");
  function updateOnline() { if (banner) banner.hidden = navigator.onLine; }
  window.addEventListener("online", updateOnline);
  window.addEventListener("offline", updateOnline);
  updateOnline();

  // Confirmation avant une action destructive : <form data-confirm="Message">
  document.addEventListener("submit", function (event) {
    var msg = event.target.getAttribute("data-confirm");
    if (msg && !window.confirm(msg)) event.preventDefault();
  });

  // Sélecteur qui recharge la page dès qu'on change de valeur : <select data-autosubmit>
  document.querySelectorAll("select[data-autosubmit]").forEach(function (select) {
    select.addEventListener("change", function () { select.form.submit(); });
  });

  // Vérification de la taille d'un fichier avant envoi : <input type="file" data-max-bytes="...">
  document.addEventListener("change", function (event) {
    var input = event.target;
    var max = parseInt(input.getAttribute("data-max-bytes"), 10);
    if (!max || !input.files) return;
    for (var i = 0; i < input.files.length; i++) {
      if (input.files[i].size > max) {
        input.setCustomValidity(input.getAttribute("data-max-message") || "Fichier trop volumineux");
        input.reportValidity();
        return;
      }
    }
    input.setCustomValidity("");
  });

  // Déconnexion : vide le cache hors ligne (appareils partagés)
  document.querySelectorAll("[data-clear-offline]").forEach(function (form) {
    form.addEventListener("submit", function () {
      try { localStorage.removeItem("offline-warm"); } catch (e) { /* ignoré */ }
      if (navigator.serviceWorker && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: "clear" });
      }
    });
  });

  // Préchargement pour la consultation hors ligne (au plus toutes les 6 heures, jamais en mode
  // « économie de données »).
  function warmOfflinePages(registration) {
    var urls = (document.body.getAttribute("data-offline-urls") || "").split(" ").filter(Boolean);
    var saveData = navigator.connection && navigator.connection.saveData;
    if (!urls.length || saveData || !navigator.onLine || !registration.active) return;
    var last = 0;
    try { last = parseInt(localStorage.getItem("offline-warm") || "0", 10); } catch (e) { /* ignoré */ }
    if (Date.now() - last < 6 * 3600 * 1000) return;
    registration.active.postMessage({ type: "warm", urls: urls });
    try { localStorage.setItem("offline-warm", String(Date.now())); } catch (e) { /* ignoré */ }
  }

  // Notifications push : bouton sur la page Notifications
  function base64ToBytes(value) {
    var padded = (value + "===".slice((value.length + 3) % 4)).replace(/-/g, "+").replace(/_/g, "/");
    var raw = atob(padded), bytes = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
    return bytes;
  }

  function postJSON(url, body) {
    var token = document.querySelector('meta[name="csrf-token"]');
    return fetch(url, {
      method: "POST", credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRFToken": token ? token.content : "" },
      body: JSON.stringify(body),
    });
  }

  function setupPush(registration) {
    var box = document.querySelector("[data-push]");
    if (!box || !("PushManager" in window) || !("Notification" in window)) return;
    var button = box.querySelector("[data-push-toggle]");
    function render(subscription) {
      button.textContent = subscription ? button.dataset.labelOff : button.dataset.labelOn;
      box.hidden = false;
    }
    registration.pushManager.getSubscription().then(render);
    button.addEventListener("click", function () {
      button.disabled = true;
      registration.pushManager.getSubscription().then(function (existing) {
        if (existing) {
          return postJSON(box.dataset.unsubscribeUrl, { endpoint: existing.endpoint })
            .then(function () { return existing.unsubscribe(); })
            .then(function () { render(null); });
        }
        return Notification.requestPermission().then(function (permission) {
          if (permission !== "granted") return;
          return registration.pushManager.subscribe({
            userVisibleOnly: true, applicationServerKey: base64ToBytes(box.dataset.vapidKey),
          }).then(function (subscription) {
            return postJSON(box.dataset.subscribeUrl, subscription.toJSON()).then(function () { render(subscription); });
          });
        });
      }).catch(function () { /* refus ou réseau : on laisse le bouton tel quel */ })
        .then(function () { button.disabled = false; });
    });
  }

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js")
        .then(function () { return navigator.serviceWorker.ready; })
        .then(function (registration) { warmOfflinePages(registration); setupPush(registration); })
        .catch(function () { /* non bloquant */ });
    });
  }
})();
