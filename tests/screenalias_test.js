// v10.152 — A ?screen= aliasok
//
// Ket app neve eltér attol, amit az ember tippelne (DNR BOX -> dnrbox,
// DNR Pub -> bar). A rossz ertek eddig CSENDBEN az alap DNR Games-t nyitotta
// meg — semmi nem jelezte az elgepelest, es percekbe telt kideriteni.
//
// FONTOS: ez a teszt HTTP-n fut, nem file://-rol. A normalizalas
// history.replaceState-tel dolgozik, ami file:// alatt nem mukodik — es a
// service worker sem regisztral ott. Ez a kulonbseg mar egyszer elrejtett elolunk
// egy egesz utat, ezert itt szandekosan valodi kiszolgalo van.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');
const ROOT = '/home/user/bottle-of-heroes';
const PORT = 8123;
const SUB = '/bottle-of-heroes';           // ugyanaz az alkonyvtar, mint a GitHub Pages-en

const MIME = { '.html':'text/html', '.js':'text/javascript', '.json':'application/json',
  '.png':'image/png', '.woff2':'font/woff2', '.mp3':'audio/mpeg', '.svg':'image/svg+xml' };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rq) => {
      let p = decodeURIComponent(req.url.split('?')[0]);
      if (!p.startsWith(SUB)) { rq.writeHead(404); return rq.end(); }
      p = p.slice(SUB.length) || '/';
      if (p.endsWith('/')) p += 'index.html';
      const f = path.join(ROOT, p);
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { rq.writeHead(404); return rq.end('nincs'); }
      rq.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(rq);
    });
    srv.listen(PORT, '127.0.0.1', () => res(srv));
  });
}

const BASE = `http://127.0.0.1:${PORT}${SUB}`;

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const srv = await serve();
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });

  const open = async (q) => {
    const p = await ctx.newPage();
    const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 110)));
    await p.route('**://**', r => r.request().url().startsWith(`http://127.0.0.1:${PORT}`) ? r.continue() : r.abort());
    await p.goto(BASE + '/' + q, { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(4200);
    const r = await p.evaluate(() => ({
      title: document.title,
      search: location.search,
      manifest: (document.querySelector('link[rel=manifest]') || {}).getAttribute
        ? document.querySelector('link[rel=manifest]').getAttribute('href').split('?')[0] : null,
      body: (document.body.innerText || '').replace(/\n/g, ' | ').slice(0, 60),
    }));
    // a Firebase CDN-t a sandbox blokkolja — az abbol jovo hiba nem a mi hibank
    r.errs = errs.filter(e => !/firebase/i.test(e));
    await p.close();
    return r;
  };

  // ── A kanonikus ertekek valtozatlanul mukodnek ──────────────────────────
  console.log('===== KANONIKUS ERTEKEK =====');
  for (const [q, title, man] of [
    ['',                'DNR Games',  'manifest.json'],
    ['?screen=dnrbox',  'DNR BOX',    'manifest-dnrbox.json'],
    ['?screen=bar',     'DNR Pub',    'manifest-bar.json'],
    ['?screen=events',  'DNR Events', 'manifest-events.json'],
    ['?screen=bingo',   'DNR Bingó',  'manifest-bingo.json'],
    ['?screen=liga',    'DNR Liga',   'manifest-liga.json'],
  ]) {
    const r = await open(q);
    ok(`${(q || '(alap)').padEnd(16)} → ${title}`, r.title === title, `${r.title} | ${r.manifest}`);
    ok(`${(q || '(alap)').padEnd(16)} → ${man}`, r.manifest === man, r.manifest);
    ok(`${(q || '(alap)').padEnd(16)} nincs JS hiba`, r.errs.length === 0, r.errs.join(' | '));
  }

  // ── Az aliasok a helyes appot nyitjak ES atirjak a cimet ────────────────
  console.log('\n===== ALIASOK =====');
  for (const [alias, canon, title, man] of [
    ['box',      'dnrbox', 'DNR BOX',   'manifest-dnrbox.json'],
    ['jukebox',  'dnrbox', 'DNR BOX',   'manifest-dnrbox.json'],
    ['pub',      'bar',    'DNR Pub',   'manifest-bar.json'],
    ['kocsma',   'bar',    'DNR Pub',   'manifest-bar.json'],
    ['stats',    'liga',   'DNR Liga',  'manifest-liga.json'],
    ['esemenyek','events', 'DNR Events','manifest-events.json'],
  ]) {
    const r = await open('?screen=' + alias);
    ok(`?screen=${alias.padEnd(10)} → ${title}`, r.title === title, `${r.title} | ${r.body}`);
    ok(`?screen=${alias.padEnd(10)} → a manifest is a helyes`, r.manifest === man, r.manifest);
    ok(`?screen=${alias.padEnd(10)} → a cim atirodik ?screen=${canon}-ra`, r.search === '?screen=' + canon, r.search);
  }

  // ── A "games"-fele aliasok a fooldalra visznek, tiszta cimmel ───────────
  console.log('\n===== FOOLDAL-ALIASOK =====');
  for (const alias of ['games', 'jatek', 'jatekok']) {
    const r = await open('?screen=' + alias);
    ok(`?screen=${alias.padEnd(9)} → DNR Games`, r.title === 'DNR Games', r.title);
    ok(`?screen=${alias.padEnd(9)} → a screen paraméter eltűnik`, r.search === '', `"${r.search}"`);
  }

  // ── Ismeretlen ertek: ne omoljon ossze, es NE irja at a cimet ───────────
  console.log('\n===== ISMERETLEN ERTEK =====');
  const unk = await open('?screen=hopphopp');
  ok('ismeretlen érték a DNR Games-t nyitja (mint eddig)', unk.title === 'DNR Games', unk.title);
  ok('a címet NEM írja át (nem tippel helyettünk)', unk.search === '?screen=hopphopp', unk.search);
  ok('nincs JS hiba', unk.errs.length === 0, unk.errs.join(' | '));

  // ── Egyeb query-parameterek megmaradnak az atiras utan is ──────────────
  console.log('\n===== EGYEB PARAMETEREK =====');
  const keep = await open('?screen=box&event=abc123');
  ok('az alias feloldodik', keep.title === 'DNR BOX', keep.title);
  ok('a tobbi paraméter megmarad', /event=abc123/.test(keep.search), keep.search);
  ok('a screen a kanonikus ertekre valt', /screen=dnrbox/.test(keep.search), keep.search);

  await b.close();
  srv.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
