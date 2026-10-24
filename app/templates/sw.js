/* Service worker ISTA : consultation hors ligne des pages déjà vues et des fichiers téléchargés. */
"use strict";

const VERSION = "{{ config.ASSET_VERSION }}";
const SHELL = "ista-shell-" + VERSION;
const PAGES = "ista-pages";
const FILES = "ista-files";
const MAX_PAGES = 80;
const MAX_FILES = 40;
const OFFLINE_URL = "{{ url_for('main.offline') }}";
const SHELL_URLS = {{ shell_urls|tojson }};

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(SHELL).then((c) => c.addAll(SHELL_URLS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("ista-shell-") && k !== SHELL).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

async function warm(urls) {
  const cache = await caches.open(PAGES);
  for (const url of urls) {
    try {
      const request = new Request(url, { credentials: "same-origin", headers: { Accept: "text/html" } });
      const response = await fetch(request);
      if (cacheable(response)) await cache.put(request, response);
    } catch (err) { /* hors ligne : on réessaiera plus tard */ }
  }
}

self.addEventListener("message", (event) => {
  const data = event.data || {};
  if (data.type === "clear") {
    event.waitUntil(Promise.all([caches.delete(PAGES), caches.delete(FILES)]));
  } else if (data.type === "warm" && Array.isArray(data.urls)) {
    const sameOrigin = data.urls.filter((u) => new URL(u, self.location.origin).origin === self.location.origin);
    event.waitUntil(warm(sameOrigin.slice(0, 10)));
  }
});

async function trim(cacheName, max) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  for (let i = 0; i < keys.length - max; i++) await cache.delete(keys[i]);
}

function cacheable(response) {
  if (!response || !response.ok || response.redirected || response.type !== "basic") return false;
  const cc = response.headers.get("Cache-Control") || "";
  return !cc.includes("no-store");
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (cacheable(response)) {
      const cache = await caches.open(PAGES);
      await cache.put(request, response.clone());
      trim(PAGES, MAX_PAGES);
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request, { ignoreVary: true });
    return cached || caches.match(OFFLINE_URL);
  }
}

async function cacheFirst(request, cacheName, max) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (cacheable(response)) {
    const cache = await caches.open(cacheName);
    await cache.put(request, response.clone());
    if (max) trim(cacheName, max);
  }
  return response;
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.startsWith("/static/")) {
    event.respondWith(cacheFirst(request, SHELL));
  } else if (url.pathname.startsWith("/fichiers/")) {
    event.respondWith(cacheFirst(request, FILES, MAX_FILES));
  } else if (request.mode === "navigate" || (request.headers.get("Accept") || "").includes("text/html")) {
    event.respondWith(networkFirst(request));
  }
});

// Notifications push (si activées par l'administration)
self.addEventListener("push", (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (err) { data = { title: event.data && event.data.text() }; }
  event.waitUntil(self.registration.showNotification(data.title || "ISTA", {
    body: data.body || "",
    icon: "{{ url_for('static', filename='img/icon-192.png') }}",
    badge: "{{ url_for('static', filename='img/icon-192.png') }}",
    data: { url: data.url || "/" },
  }));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = new URL(event.notification.data.url || "/", self.location.origin);
  if (target.origin !== self.location.origin) return;
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((windows) => {
      for (const w of windows) {
        if ("focus" in w) { w.navigate(target.href); return w.focus(); }
      }
      return self.clients.openWindow(target.href);
    })
  );
});
