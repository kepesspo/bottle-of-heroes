#!/usr/bin/env node
// ── Bottle of Heroes build ──────────────────────────────────────────────────
// app.src.html (forrás, böngészőben is futtatható dev változat)
//   → index.html (kiszolgált, ELŐFORDÍTOTT — nincs böngészőbeli Babel)
//   → sw.js     (cache service worker, verziózott)
//
// Futtatás:  node build.js
// Függőség:  NINCS — a fordító maga a forrásba ágyazott @babel/standalone.
//
// Mit csinál:
//  1. a <script type="text/babel"> JSX-et lefordítja sima JS-re (preset: react)
//  2. a react/react-dom development buildeket kicseréli a vendor/ production
//     buildekre (kisebb + futásidőben is gyorsabb)
//  3. a 3 MB-os Babel-standalone scriptet teljesen eltávolítja
//  4. sw.js-t generál az APP_VERSION-höz kötött cache névvel

const fs = require('fs');
const vm = require('vm');

const SRC = 'app.src.html';
const OUT = 'index.html';

let src = fs.readFileSync(SRC, 'utf8');

// Verzió a FORRÁSBÓL (a fordított/tömörített kódban már más a formátum)
const verMatch = src.match(/const APP_VERSION = '(v[\d.]+)';/);
if (!verMatch) throw new Error('APP_VERSION nem található az app.src.html-ben');
const version = verMatch[1];

// ── segéd: inline script blokk keresése tartalom-aláírás alapján ────────────
function findScript(signature, from = 0) {
  const sig = src.indexOf(signature, from);
  if (sig < 0) throw new Error('Nem találom a scriptet: ' + signature.slice(0, 60));
  const open = src.lastIndexOf('<script', sig);
  const openEnd = src.indexOf('>', open) + 1;
  const close = src.indexOf('</script>', sig);
  return { open, openEnd, close, closeEnd: close + '</script>'.length, inner: src.slice(openEnd, close) };
}

// 1) Babel-standalone kiemelése (ez lesz a fordítónk), majd törlése
const BABEL_SIG = '!function(e,t){"object"==typeof exports&&"undefined"!=typeof module?t(exports):';
const babelSeg = findScript(BABEL_SIG);
console.log('Babel-standalone megtalálva:', Math.round(babelSeg.inner.length / 1024), 'KB');

const sandbox = { exports: {}, console, setTimeout, clearTimeout, process: { env: {} } };
sandbox.window = sandbox;
sandbox.self = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(babelSeg.inner, sandbox, { filename: 'babel-standalone.js' });
const Babel = sandbox.Babel || sandbox.exports;
if (!Babel || typeof Babel.transform !== 'function') throw new Error('Babel betöltése nem sikerült');
console.log('Babel verzió:', Babel.version);

// 2) Az app JSX lefordítása
const appSeg = findScript('const { useState, useEffect, useRef, useMemo } = React;');
console.log('App JSX:', Math.round(appSeg.inner.length / 1024), 'KB');
const t0 = Date.now();
const compiled = Babel.transform(appSeg.inner, {
  presets: ['react'],
  compact: true,
  comments: false,
}).code;
console.log('Fordítás kész:', ((Date.now() - t0) / 1000).toFixed(1) + 's →', Math.round(compiled.length / 1024), 'KB');

// csere: type="text/babel" → sima script a fordított kóddal
src = src.slice(0, appSeg.open) + '<script>\n' + compiled + '\n' + src.slice(appSeg.close);

// 3) Babel-standalone blokk törlése (újrakeresés, mert az indexek eltolódtak)
const babelSeg2 = findScript(BABEL_SIG);
src = src.slice(0, babelSeg2.open) + '<!-- babel-standalone eltávolítva (előfordított build) -->' + src.slice(babelSeg2.closeEnd);

// 4) React production buildek
const reactProd = fs.readFileSync('vendor/react.production.min.js', 'utf8');
const reactDomProd = fs.readFileSync('vendor/react-dom.production.min.js', 'utf8');
const rSeg = findScript('react.development.js');
src = src.slice(0, rSeg.openEnd) + '\n' + reactProd + '\n' + src.slice(rSeg.close);
const rdSeg = findScript('react-dom.development.js');
src = src.slice(0, rdSeg.openEnd) + '\n' + reactDomProd + '\n' + src.slice(rdSeg.close);

// 5) Figyelmeztető fejléc
src = src.replace(/^(<!DOCTYPE html>\s*\n?)/i,
  '$1<!-- ════ GENERÁLT FÁJL — NE SZERKESZD KÉZZEL! ════\n' +
  '     Forrás: app.src.html · Build: node build.js · ' + version + ' ════ -->\n');

fs.writeFileSync(OUT, src);
console.log(OUT, 'kiírva:', (src.length / 1024 / 1024).toFixed(2), 'MB |', version);

// 6) sw.js generálása
const sw = `// GENERÁLT FÁJL — forrás: build.js (node build.js)
const CACHE = 'boh-${version}';

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(['./', 'index.html']).catch(() => {})));
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
    if (!/(gstatic\\.com|jsdelivr\\.net|cdnjs\\.cloudflare\\.com)$/.test(url.hostname) &&
        !/gstatic|jsdelivr|cdnjs/.test(url.hostname)) return;
    e.respondWith(
      caches.open(CACHE).then((c) =>
        c.match(req).then((hit) => hit || fetch(req).then((res) => { c.put(req, res.clone()).catch(() => {}); return res; }))
      )
    );
    return;
  }

  const isNav = req.mode === 'navigate' || /(?:^|\\/)index\\.html$/.test(url.pathname) || url.pathname.endsWith('/');
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
`;
fs.writeFileSync('sw.js', sw);
console.log('sw.js kiírva (cache: boh-' + version + ')');
