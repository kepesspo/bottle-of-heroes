// Cache name automatikusan frissül — a html injektálja a verziót query paramként
// sw.js?v=9.625 → CACHE = 'boh-9.625'
const params = new URLSearchParams(self.location.search);
const ver = params.get('v') || 'dev';
const CACHE = `boh-${ver}`;

const ASSETS = [
  '/bottle-of-heroes/',
  '/bottle-of-heroes/index.html',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;

  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(resp => {
        if (resp.ok) {
          const clone = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return resp;
      });
    })
  );
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    const focused = cs.find(c => c.focused);
    if (focused) return focused.focus();
    if (cs.length) return cs[0].focus();
    return clients.openWindow('/bottle-of-heroes/');
  }));
});
