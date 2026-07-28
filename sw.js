// GENERÁLT FÁJL — forrás: build.js (node build.js)
const CACHE = 'boh-v10.172';

self.addEventListener('install', (e) => {
  // A betutipus is elore a cache-be: sajat domainrol jon (nem Google Fonts),
  // igy a nyito kepernyo rossz haloval / offline is a helyes fonttal jelenik meg.
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll([
    './', 'index.html',
    'assets/fonts/nunito-latin.woff2', 'assets/fonts/nunito-latin-ext.woff2',
  ]).catch(() => {})));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return; // Firestore írások/streamek érintetlenek
  const url = new URL(req.url);

  // Cross-origin: csak az ismert CDN-eket cache-eljük (cache-first)
  if (url.origin !== location.origin) {
    if (!/(gstatic\.com|jsdelivr\.net|cdnjs\.cloudflare\.com)$/.test(url.hostname) &&
        !/gstatic|jsdelivr|cdnjs/.test(url.hostname)) return;
    e.respondWith(
      caches.open(CACHE).then((c) =>
        c.match(req).then((hit) => hit || fetch(req).then((res) => { c.put(req, res.clone()).catch(() => {}); return res; }))
      )
    );
    return;
  }

  const isNav = req.mode === 'navigate' || /(?:^|\/)index\.html$/.test(url.pathname) || url.pathname.endsWith('/');
  if (isNav) {
    // stale-while-revalidate: azonnal a cache-ből indul, háttérben frissít,
    // változásnál üzen az oldalnak (frissítés-sáv)
    e.respondWith(
      caches.open(CACHE).then(async (c) => {
        const cached = await c.match('index.html');
        const network = fetch(req).then(async (res) => {
          if (res && res.ok) {
            const forCache = res.clone();
            const forDiff = res.clone();
            await c.put('index.html', forCache);
            if (cached) {
              const [a, b] = await Promise.all([cached.clone().text(), forDiff.text()]);
              if (a !== b) {
                const cs = await self.clients.matchAll({ includeUncontrolled: true });
                cs.forEach((cl) => cl.postMessage({ type: 'boh-update' }));
              }
            }
          }
          return res;
        }).catch(() => null);
        return cached || network.then((r) => r || new Response('Offline', { status: 503 }));
      })
    );
    return;
  }

  // Same-origin assetek (képek, manifest, mp3): cache-first + háttér frissítés
  e.respondWith(
    caches.open(CACHE).then((c) =>
      c.match(req).then((hit) => {
        const net = fetch(req).then((res) => {
          if (res && res.ok) c.put(req, res.clone()).catch(() => {});
          return res;
        }).catch(() => null);
        return hit || net.then((r) => r || new Response('', { status: 504 }));
      })
    )
  );
});
