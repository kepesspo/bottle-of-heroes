// v10.421 — EGY téma-felület az összes apphoz (config/appThemes).
//
// Fogódzók:
//  1) mentett beállítás NÉLKÜL a régi forrás él: a központ/Games az eszköz boh_theme-je,
//     az Events a régi Events-témája (kontroll — enélkül a frissítés mindenkinek átszínezne)
//  2) közös téma + app-saját: a központ a közöset, a központból nyitott Events a SAJÁTJÁT
//     viseli (eddig az appon belül a Games eszköz-témáját), a Games megint a közöset
//  3) deep link (?screen=events) a gyorsítótárból már a boot-ban a jó témával indul,
//     a nyitókép (splash) is
//  4) Admin → Általános → Témák: közös téma, app-saját, „Közös", „Mindenhol a közös" — mind
//     azonnal a config/appThemes-be ír
//  5) régi állapot az első mentéskor PONTOSAN úgy kerül be, ahogy látszott (Events saját)
//  6) az admin szerkezete: van Témák fül, nincs Pub/BOX kategória és Events-téma fül; a
//     Games beállítás-lapján nincs többé téma-választó
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

async function open(b, q, cfg, ls, vp) {
  const p = await b.newPage({ viewport: vp || { width: 390, height: 844 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(({ cfg, ls }) => {
    try { localStorage.setItem('boh_onboarded', '1'); Object.keys(ls || {}).forEach(k => localStorage.setItem(k, ls[k])); } catch(e) {}
    const docs = Object.assign({}, (cfg && cfg.__legacy) || {});
    if (cfg && !cfg.__legacy) docs.appThemes = cfg;
    window.__fbStore.config = Object.assign(window.__fbStore.config || {}, docs);
  }, { cfg, ls: Object.assign({ boh_splash: '0' }, ls || {}) });
  await p.goto('file://' + ROOT + '/index.html' + q, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3300);
  return p;
}
// a gyökér konténer háttere = a képernyő témája (a statuszsáv is ebből fest)
const rootBg = p => p.evaluate(() => getComputedStyle(document.querySelector('[data-theme]')).backgroundColor);
const themeAttr = p => p.evaluate(() => document.querySelector('[data-theme]').getAttribute('data-theme'));
const rgb = hex => { const h = hex.replace('#', ''); return `rgb(${parseInt(h.slice(0,2),16)}, ${parseInt(h.slice(2,4),16)}, ${parseInt(h.slice(4,6),16)})`; };
const openCard = async (p, key) => {
  for (let i = 0; i < 2; i++) {
    await p.evaluate(k => { const c = document.querySelector(`[data-hub-card="${k}"]`); const b = c && [...c.querySelectorAll('button')].find(x => /Megnyitás/.test(x.textContent)); b && b.click(); }, key);
    await p.waitForTimeout(700);
  }
};

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const TH = await (async () => { const p = await open(b, '', null); const t = await p.evaluate(() => Object.fromEntries(Object.keys(THEMES).map(k => [k, THEMES[k].bg]))); await p.close(); return t; })();

  console.log('\n===== 1. RÉGI ÁLLAPOT (nincs mentett beállítás) =====');
  // a régi Events-téma a Firestore-ban is ott ül (config/eventsTheme) — a BottleApp onnan frissíti a gyorsítótárat
  let p = await open(b, '', { __legacy: { eventsTheme: { theme: 'slate' } } }, { boh_theme: 'jade', boh_events_theme: 'slate' });
  ok((await themeAttr(p)) === 'jade' && (await rootBg(p)) === rgb(TH.jade), 'a központ az eszköz régi témáját viseli (jade)', await themeAttr(p));
  await openCard(p, 'log');
  ok((await themeAttr(p)) === 'slate', 'az Events a saját régi témáját (slate)', await themeAttr(p));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 2. KÖZÖS + APP-SAJÁT =====');
  const CFG = { default: 'ice', apps: { events: 'dark' } };
  p = await open(b, '', CFG, { boh_theme: 'jade' });
  ok((await themeAttr(p)) === 'ice' && (await rootBg(p)) === rgb(TH.ice), '⚠️ a központ a KÖZÖS témát viseli (ice), nem az eszközét', await themeAttr(p));
  await openCard(p, 'log');
  ok((await themeAttr(p)) === 'dark' && (await rootBg(p)) === rgb(TH.dark), '⚠️ a központból nyitott Events a SAJÁT témáját (dark)', await themeAttr(p));
  await p.evaluate(() => { const bb = document.querySelector('.appbar-shell button'); bb && bb.click(); }); await p.waitForTimeout(800);
  await openCard(p, 'home');
  ok((await themeAttr(p)) === 'ice', 'a Games megint a közöset', await themeAttr(p));
  const tc = await p.evaluate(() => document.querySelector('meta[name="theme-color"]').getAttribute('content'));
  ok(tc && tc.toUpperCase() === TH.ice.toUpperCase(), 'a theme-color meta is követi', tc);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 3. DEEP LINK + NYITÓKÉP =====');
  p = await b.newPage({ viewport: { width: 390, height: 844 } });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(c => { try { localStorage.setItem('boh_onboarded', '1'); localStorage.setItem('boh_splash', '1'); localStorage.setItem('boh_app_themes', JSON.stringify(c)); } catch(e) {}
    window.__fbStore.config = Object.assign(window.__fbStore.config || {}, { appThemes: c }); }, CFG);
  await p.goto('file://' + ROOT + '/index.html?screen=events', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(250);
  const sp = await p.evaluate(() => { const s = document.getElementById('splash'); return s ? getComputedStyle(s).backgroundColor : null; });
  ok(sp === rgb(TH.dark), '⚠️ a nyitókép már az Events saját témájával (dark) indul', sp);
  await p.waitForTimeout(4500);
  ok((await themeAttr(p)) === 'dark', 'a deep link is a saját témát viseli', await themeAttr(p));
  await p.close();

  console.log('\n===== 4. ADMIN → TÉMÁK =====');
  p = await open(b, '?screen=games', { default: 'warm', apps: {} }, null, { width: 2000, height: 1100 });
  await p.evaluate(() => { document.getElementById('root').style.display = 'none'; const d = document.createElement('div'); d.id = '__a'; d.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column'; document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(window.AdminScreen, { go:()=>{}, setTheme:()=>{}, currentTheme:'warm' })); });
  await p.waitForTimeout(1200);
  const nav = await p.evaluate(() => ({ cats: [...document.querySelectorAll('#__a [data-admin-nav] > [data-admin-cat]')].map(x => x.getAttribute('data-admin-cat')).join(), themes: !!document.querySelector('#__a [data-admin-tab="themes"]'), evTheme: !!document.querySelector('#__a [data-admin-tab="eventsTheme"]') }));
  ok(nav.themes && !nav.evTheme && !/box|pub/.test(nav.cats), 'egy Témák fül az Általánosban; nincs Pub/BOX kategória és Events-téma fül', JSON.stringify(nav));
  await p.evaluate(() => document.querySelector('#__a [data-admin-tab="themes"]').click()); await p.waitForTimeout(600);
  const rows = await p.evaluate(() => [...document.querySelectorAll('#__a [data-theme-app]')].map(x => x.getAttribute('data-theme-app')).join());
  ok(rows === 'hub,games,events,torta,tipp,bingo,box,pub,liga', 'mind a kilenc app egy listán', rows);
  const store = () => p.evaluate(() => JSON.parse(JSON.stringify(window.__fbStore.config.appThemes || null)));
  await p.evaluate(() => document.querySelector('#__a [data-theme-default="jade"]').click()); await p.waitForTimeout(400);
  ok((await store()).default === 'jade', 'a közös téma azonnal ment (jade)', JSON.stringify(await store()));
  await p.evaluate(() => document.querySelector('#__a [data-theme-app="pub"] [data-theme-pick="slate"]').click()); await p.waitForTimeout(400);
  let st = await store();
  ok(st.apps.pub === 'slate' && st.default === 'jade', 'a Pub saját témát kap (slate), a közös marad', JSON.stringify(st));
  ok(/Saját: /.test(await p.evaluate(() => document.querySelector('#__a [data-theme-app="pub"] [data-theme-eff]').innerText)), 'a sor kiírja: „Saját: …"');
  await p.evaluate(() => document.querySelector('#__a [data-theme-app="liga"] [data-theme-pick="dark"]').click()); await p.waitForTimeout(300);
  await p.evaluate(() => document.querySelector('#__a [data-theme-app="pub"] [data-theme-pick=""]').click()); await p.waitForTimeout(400);
  st = await store();
  ok(!('pub' in st.apps) && st.apps.liga === 'dark', '„Közös" visszaállítja a Pubot, a Liga marad', JSON.stringify(st));
  await p.evaluate(() => document.querySelector('#__a [data-theme-reset]').click()); await p.waitForTimeout(400);
  st = await store();
  ok(Object.keys(st.apps).length === 0 && st.default === 'jade', '„Mindenhol a közös" minden saját témát töröl', JSON.stringify(st));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 5. RÉGI ÁLLAPOT ELSŐ MENTÉSE =====');
  p = await open(b, '?screen=games', { __legacy: { eventsTheme: { theme: 'slate' } } }, { boh_theme: 'warm', boh_events_theme: 'slate', boh_bar_theme: 'warm' }, { width: 2000, height: 1100 });
  await p.evaluate(() => { document.getElementById('root').style.display = 'none'; const d = document.createElement('div'); d.id = '__a'; d.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column'; document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(window.AdminScreen, { go:()=>{}, setTheme:()=>{}, currentTheme:'warm' })); });
  await p.waitForTimeout(1200);
  await p.evaluate(() => document.querySelector('#__a [data-admin-tab="themes"]').click()); await p.waitForTimeout(600);
  ok(/Saját: Mélytenger/.test(await p.evaluate(() => document.querySelector('#__a [data-theme-app="events"] [data-theme-eff]').innerText)), 'a mentetlen régi Events-téma sajátként látszik');
  await p.evaluate(() => document.querySelector('#__a [data-theme-app="liga"] [data-theme-pick="ice"]').click()); await p.waitForTimeout(400);
  st = await store();
  ok(st && st.default === 'warm' && st.apps.events === 'slate' && st.apps.liga === 'ice', '⚠️ az első mentés a látott állapotot írja ki (Events saját marad)', JSON.stringify(st));
  await p.close();

  console.log('\n===== 6. NINCS TÖBBÉ ESZKÖZÖNKÉNTI TÉMA-VÁLASZTÓ =====');
  p = await open(b, '?screen=games', null);
  // v10.425 óta a Beállítások lap megszűnt — a helyén a Kiegészítők; ott sincs téma-választó
  await p.evaluate(() => { const g = document.querySelector('[data-home-tools]'); g && g.click(); });
  await p.waitForTimeout(700);
  const sheet = await p.evaluate(() => document.body.innerText);
  ok(/Betűsorsoló/.test(sheet) && !/TÉMÁK|Témák/.test(sheet), 'a Games fejlécéből nyíló lapon nincs téma-választó (a lap megnyílt)', sheet.slice(0, 60).replace(/\n/g, ' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
