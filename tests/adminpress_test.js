// v10.149 — Admin megnyitása hosszú nyomással (2 mp)
//
// Valós órán mérve: a 2 mp nem lehet "kb.". Ha rövidebb, véletlenül nyílik meg
// a fogaskerékre koppintva; ha hosszabb, a felhasználó elengedi, mielőtt kész.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

const seed = `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  window.__fbStore['profiles'] = { p_a:{name:'Alfa',color:'#5BA0DB'} };
  window.__fbStore['stats'] = {}; window.__fbStore['game_stats'] = {};
  window.__fbStore['statEvents'] = {}; window.__fbStore['gameStatEvents'] = {};
  window.__fbStore['seasons'] = {}; window.__fbStore['config'] = {}; window.__fbStore['usage'] = {};
`;

async function home(b) {
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);
  p.__errs = errs;
  return p;
}

// A fogaskerek: a jobb felso pill elso gombja
const gearBox = (p) => p.evaluate(() => {
  const btn = Array.from(document.querySelectorAll('button')).find(x => {
    const r = x.getBoundingClientRect();
    return Math.abs(r.width - 52) < 2 && Math.abs(r.height - 52) < 2 && r.top < 80 && x.querySelector('svg circle');
  });
  if (!btn) return null;
  const r = btn.getBoundingClientRect();
  return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
});
// A korgyuru csak nyomas kozben letezik — ez jelzi, hogy fut a szamlalo
const ringPct = (p) => p.evaluate(() => {
  const c = Array.from(document.querySelectorAll('svg circle'))
    .find(x => x.getAttribute('stroke-dasharray') && x.closest('button'));
  if (!c) return null;
  const total = parseFloat(c.getAttribute('stroke-dasharray'));
  const off = parseFloat(c.getAttribute('stroke-dashoffset'));
  return Math.round((1 - off / total) * 100);
});
const pinOpen = (p) => p.evaluate(() => /PIN|Admin belépés|admin/i.test(document.body.innerText) &&
  !!document.querySelector('input[type="password"]'));

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  console.log('===== HOSSZU NYOMAS: 2 MP =====');
  let p = await home(b);
  const g = await gearBox(p);
  ok('megvan a fogaskerek gomb a fejlecben', !!g, JSON.stringify(g));
  if (!g) { await b.close(); process.exit(1); }

  // ── 1,5 mp: MEG NEM nyilhat meg ────────────────────────────────────────
  await p.mouse.move(g.x, g.y);
  await p.mouse.down();
  await p.waitForTimeout(700);
  const midRing = await ringPct(p);
  ok('nyomás közben fut a körgyűrű', midRing != null && midRing > 20 && midRing < 60, `${midRing}%`);
  await p.waitForTimeout(800);            // osszesen ~1,5 mp
  ok('1,5 mp-nél MÉG NEM nyílt meg', (await pinOpen(p)) === false);
  await p.mouse.up();
  await p.waitForTimeout(300);
  ok('elengedésre eltűnik a körgyűrű', (await ringPct(p)) === null);
  ok('elengedés után sem nyílt meg', (await pinOpen(p)) === false);

  await p.close();

  // ── 2 mp: meg KELL nyilnia ─────────────────────────────────────────────
  // FONTOS: friss lap. Az elozo nyomas elengedese `click`-et is kivalt, ami
  // megnyitja a Beallitasokat — az pedig eltakarja a fogaskereket.
  p = await home(b);
  const g2 = await gearBox(p);
  await p.mouse.move(g2.x, g2.y);
  const t0 = Date.now();
  await p.mouse.down();
  let opened = false, elapsed = null;
  for (let i = 0; i < 40; i++) {
    await p.waitForTimeout(100);
    if (await pinOpen(p)) { opened = true; elapsed = Date.now() - t0; break; }
  }
  await p.mouse.up();
  ok('hosszú nyomásra megnyílik', opened);
  ok('2 mp körül nyílik (1,9–2,5 mp)', elapsed != null && elapsed >= 1900 && elapsed <= 2500, `${elapsed} ms`);

  // ── Rovid koppintas a beallitasokat nyitja, NEM az admint ──────────────
  await p.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(x => /Bezár|Mégse|×|✕/.test(x.innerText || ''));
    if (btn) btn.click();
  });
  await p.waitForTimeout(600);
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.screenshot({ path: __dirname + '/adminpress.png' });
  await p.close();

  // ── Az al-fulek arnyeka a PIRULARA legyen szabva ────────────────────────
  // A T.shadow kartyara van hangolva (12px-re tolt, 28px szorasu reteg). Kis
  // pirulan az elszakad a gombtol, es a szomszedok arnyeka egy savva folyik
  // ossze — a kepen ugy nezett ki, mintha a konteneré volna.
  console.log('\n===== AL-FUL PIRULAK ARNYEKA =====');
  p = await home(b);
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__ad';
    root.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column;background:' + ((window._T && window._T.bg) || '#EFC77A');
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(window.AdminScreen, { go:()=>{}, setTheme:()=>{}, currentTheme:'classic' }));
  });
  await p.waitForTimeout(1200);
  const sh = await p.evaluate(() => {
    const row = Array.from(document.querySelectorAll('#__ad div')).find(d => d.style.overflowX === 'auto');
    if (!row) return null;
    const pills = Array.from(row.querySelectorAll('button'));
    const inactive = pills.find(x => getComputedStyle(x).boxShadow !== 'none');
    const active = pills.find(x => getComputedStyle(x).boxShadow === 'none');
    const css = inactive ? getComputedStyle(inactive).boxShadow : '';
    // a leghosszabb px-ertek az arnyekban (eltolas vagy szoras)
    const maxPx = Math.max(0, ...(css.match(/-?\d+(\.\d+)?px/g) || []).map(v => Math.abs(parseFloat(v))));
    const pillH = inactive ? Math.round(inactive.getBoundingClientRect().height) : 0;
    return { n: pills.length, hasActiveFlat: !!active, css, maxPx, pillH,
             rowPadBottom: getComputedStyle(row).paddingBottom };
  });
  ok('megvannak az al-ful pirulak', sh && sh.n >= 3, JSON.stringify(sh && sh.n));
  ok('a kivalasztott pirula lapos marad', sh && sh.hasActiveFlat);
  ok('az arnyek NEM a kartya-arnyek (nincs 28px szoras)', sh && !/28px/.test(sh.css), sh && sh.css);
  ok('az arnyek a pirula magassagahoz merten kicsi (<= 8px)', sh && sh.maxPx <= 8, `${sh && sh.maxPx}px, pirula ${sh && sh.pillH}px`);
  ok('a sor also paddingje is egyutt szukult', sh && sh.rowPadBottom === '7px', sh && sh.rowPadBottom);
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
