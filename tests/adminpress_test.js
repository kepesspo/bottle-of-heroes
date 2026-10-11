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

async function home(b, q) {
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed);
  await p.goto(BASE + (q === undefined ? '?screen=games' : q), { waitUntil: 'domcontentloaded' });  // v10.409: a Games főoldaláról (a nyitóképernyő a DNR központ)
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

  // v10.410: az admin-belépő a DNR KÖZPONT fejlécébe költözött (tulajdonosi kérés:
  // „onnan szeretném irányítani"). Koppintásra PIN, a Games fogaskereke már csak a
  // Beállítások — hosszú nyomásra sem nyit admint.
  console.log('===== ADMIN A DNR KÖZPONTBÓL =====');
  let p = await home(b, '');
  const ab = await p.evaluate(() => { const x = document.querySelector('[data-hub-admin]'); if (!x) return null; const r = x.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2, top: r.top }; });
  ok('a központ fejlécében ott az admin gomb', !!ab && ab.top < 80, JSON.stringify(ab));
  if (!ab) { await b.close(); process.exit(1); }
  // valódi egérkattintás (hit-test), nem element.click()
  await p.mouse.click(ab.x, ab.y);
  await p.waitForTimeout(400);
  ok('koppintásra megnyílik a PIN', await pinOpen(p));
  await p.fill('[data-admin-pin] input', '1111'); await p.keyboard.press('Enter');
  await p.waitForTimeout(200);
  ok('rossz PIN: hibaüzenet, marad a központ', await p.evaluate(() => /Helytelen PIN/.test(document.body.innerText) && !!document.querySelector('[data-dnr-hub]')));
  await p.fill('[data-admin-pin] input', '199509'); await p.keyboard.press('Enter');
  await p.waitForTimeout(900);
  ok('helyes PIN → Admin', await p.evaluate(() => !document.querySelector('[data-dnr-hub]') && /Admin/.test(document.body.innerText)));
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => { const r = x.getBoundingClientRect(); return r.top < 140 && r.left < 80 && r.width > 0 && x.querySelector('svg'); }); b && b.click(); });
  await p.waitForTimeout(900);
  ok('az Admin vissza gombja a KÖZPONTBA visz', await p.evaluate(() => !!document.querySelector('[data-dnr-hub]')));
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.close();

  console.log('\n===== GAMES FOGASKERÉK: CSAK BEÁLLÍTÁSOK =====');
  p = await home(b);
  const g = await gearBox(p);
  ok('megvan a fogaskerek gomb a Games fejlecben', !!g, JSON.stringify(g));
  await p.mouse.move(g.x, g.y);
  await p.mouse.down();
  await p.waitForTimeout(2600);
  ok('2,6 mp nyomásra SEM nyílik admin PIN (átköltözött)', (await pinOpen(p)) === false);
  await p.mouse.up();
  await p.waitForTimeout(500);
  ok('koppintás/elengedés a Beállításokat nyitja', await p.evaluate(() => /Beállítások|Settings/.test(document.body.innerText)));
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

  // ── v10.415: széles kijelzőn oldalsáv + keskeny tartalom, és olvasható mezők ──
  console.log('\n===== ADMIN WEBEN: OLDALSÁV + KESKENY OSZLOP =====');
  p = await b.newPage({ viewport: { width: 2000, height: 1075 } });
  p.__errs = []; p.on('pageerror', e => p.__errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub); await p.addInitScript(seed);
  await p.goto(BASE + '?screen=games', { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(3000);
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const d = document.createElement('div'); d.id = '__aw'; d.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column';
    document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(window.AdminScreen, { go:()=>{}, setTheme:()=>{}, currentTheme:'classic' }));
  });
  await p.waitForTimeout(1000);
  await p.evaluate(() => document.querySelector('[data-admin-tab="settings"]').click());
  await p.waitForTimeout(600);
  const wl = await p.evaluate(() => {
    const nav = document.querySelector('[data-admin-nav]'), body = document.querySelector('[data-admin-body]');
    const inp = body && body.querySelector('input:not([type=checkbox])');
    const rn = nav.getBoundingClientRect(), rb = body.getBoundingClientRect();
    return { tabs: nav.querySelectorAll('[data-admin-tab]').length, bodyW: Math.round(rb.width), gap: Math.round(rb.left - rn.right),
             inpBg: inp ? getComputedStyle(inp).backgroundColor : null, surface: (window._T || {}).surface || null };
  });
  ok('oldalsáv az összes füllel (17 — v10.419 óta a Tipp és a Tortán külön fül)', wl.tabs === 17, JSON.stringify(wl));
  ok('⚠️ a tartalom keskeny (≤ 820 px), nem nyúlik a 2000 px-es képernyőre', wl.bodyW <= 820, JSON.stringify(wl));
  ok('az oldalsáv és a tartalom egymás mellett (nincs nagy rés)', wl.gap >= 0 && wl.gap <= 40, JSON.stringify(wl));
  ok('⚠️ a mező háttere nem a téma narancsa (fehér/felület)', /rgb\(255, 255, 255\)/.test(wl.inpBg || ''), wl.inpBg);
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
