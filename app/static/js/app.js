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
      if (navigator.serviceWorker && navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: "clear" });
      }
    });
  });

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function () { /* non bloquant */ });
    });
  }
})();
