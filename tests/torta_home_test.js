// v10.402 — DNR a tortán a főképernyőn: ikon + a beállítás-kapcsoló
// v10.409 óta a „főképernyő" a DNR KÖZPONT (DnrHubScreen).
// v10.419 óta a Bingó, a Tipp és a Tortán KÜLÖN app: saját csempe, saját láthatóság
// (`bingoConfig.apps.<app>`), saját admin-fül. A régi config (enabled + mode, `apps`
// nélkül) a régi szabály szerint látszik: CSAK a kiválasztott mód appja.
//
// Fogódzók:
//  1) régi config (mode=torta, apps nélkül) → a központban CSAK a Tortán csempe, a torta-logóval
//  2) a „Melyik app látszódjon" listán mind a HÁROM app külön sor
//  3) ⚠️ homeConfig.dnrApps.torta = false → a Tortán csempe eltűnik
//  4) a régi ?screen=bingo ikon emlékezete (boh_bingo_mode) a Tortánra mutat
//  5) apps: mindhárom BE → három csempe, sorrendben Tortán · Tipp · Bingó
//  6) az app admin-fülének kapcsolója AZONNAL rejt, a teljes apps térképet írja ki
//  7) sikertelen mentés nem ír „Mentve"-t
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const TORTA = 'assets/dnr_torta_mark.png',   // v10.423: az egységes ikoncsalád jele
      BINGO = 'assets/dnr_bingo_icon.png';

const TIPP = 'assets/dnr_tipp_icon.png';
const card = (p, key) => p.evaluate(key => {
  const b = document.querySelector(`#__h [data-hub-card="${key}"]`);
  if (!b) return null;
  const i = b.querySelector('img'); return { txt: (b.textContent || '').trim(), src: i ? i.getAttribute('src') : null };
}, key);
const hubKeys = p => p.evaluate(() => [...document.querySelectorAll('#__h [data-hub-card]')].map(x => x.getAttribute('data-hub-card')));
const setRows = p => p.evaluate(() => [...document.querySelectorAll('#__s img')].map(i => ({ src: i.getAttribute('src'), txt: ((i.parentElement || {}).textContent || '').trim() })));
const setDoc = (p, doc, data) => p.evaluate(({ doc, data }) => firebase.firestore().collection('config').doc(doc).set(data), { doc, data });

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1400 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(() => {
    window.__fbStore['config'] = Object.assign(window.__fbStore['config'] || {}, {
      bingoConfig: { enabled: true, mode: 'torta', tortaTitle: 'DNR a tortán' },
      homeConfig: { dnrAppsEnabled: true },
    });
    try { localStorage.removeItem('boh_bingo_mode'); } catch(e) {}
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const mk = (id, left) => { const d = document.createElement('div'); d.id = id;
      d.style.cssText = `position:absolute;left:${left}px;top:0;width:402px;height:1400px;overflow:auto;z-index:9;background:#fff;display:flex;flex-direction:column`;
      document.body.appendChild(d); return ReactDOM.createRoot(d); };
    mk('__h', 0).render(React.createElement(DnrHubScreen, { onOpen: () => {} }));
    mk('__s', 410).render(React.createElement(AdminHomeToggles));
  });
  await p.waitForTimeout(1200);

  console.log('\n===== 1. RÉGI CONFIG: CSAK A TORTÁN =====');
  ok(JSON.stringify((await hubKeys(p)).filter(k => ['bingo','tipp','torta'].includes(k))) === '["torta"]', '⚠️ régi config (mode=torta, apps nélkül) → csak a Tortán csempe', JSON.stringify(await hubKeys(p)));
  const tc = await card(p, 'torta');
  ok(tc && tc.src === TORTA && /DNR a tortán/.test(tc.txt), 'a Tortán csempe a torta-logót és a TELJES nevet viszi', JSON.stringify(tc));

  console.log('\n===== 2. BEÁLLÍTÁSOK: HÁROM KÜLÖN SOR =====');
  const rows = await setRows(p);
  ok(rows.some(r => r.src === BINGO && /DNR Bingó/.test(r.txt)) && rows.some(r => r.src === TIPP && /DNR Tipp/.test(r.txt)) && rows.some(r => r.src === TORTA && /DNR a tortán/.test(r.txt)),
     '⚠️ a „Melyik app látszódjon" listán a Bingó, a Tipp és a Tortán külön sor', JSON.stringify(rows.map(r => r.txt)));

  console.log('\n===== 3. KIKAPCSOLVA ELTŰNIK =====');
  await setDoc(p, 'homeConfig', { dnrAppsEnabled: true, dnrApps: { torta: false } });
  await p.waitForTimeout(600);
  ok((await card(p, 'torta')) === null, '⚠️ dnrApps.torta=false → a Tortán csempe eltűnt');
  await setDoc(p, 'homeConfig', { dnrAppsEnabled: true });
  await p.waitForTimeout(600);
  ok(!!(await card(p, 'torta')), 'visszakapcsolva újra ott (kontroll)');

  console.log('\n===== 4. A RÉGI ?screen=bingo IKON EMLÉKEZETE =====');
  ok((await p.evaluate(() => localStorage.getItem('boh_bingo_mode'))) === 'torta', 'boh_bingo_mode = torta (a régi telepített ikon a Tortánt nyitja)');

  console.log('\n===== 5. MINDHÁROM BE =====');
  await setDoc(p, 'bingoConfig', { enabled: true, mode: 'torta', tortaTitle: 'DNR a tortán', apps: { bingo: true, tipp: true, torta: true } });
  await p.waitForTimeout(700);
  const ks = (await hubKeys(p)).filter(k => ['bingo','tipp','torta'].includes(k));
  ok(JSON.stringify(ks) === '["torta","tipp","bingo"]', '⚠️ három külön csempe: Tortán · Tipp · Bingó', JSON.stringify(ks));
  ok(((await card(p, 'tipp')) || {}).src === TIPP && ((await card(p, 'bingo')) || {}).src === BINGO, 'a Tipp és a Bingó a saját ikonját viszi');
  ok((await p.evaluate(() => localStorage.getItem('boh_bingo_mode'))) === 'bingo', 'a Bingó be van kapcsolva → a ?screen=bingo már a Bingót nyitja');

  console.log('\n===== 6. ADMIN → TORTÁN: A KAPCSOLÓ AZONNAL REJT =====');
  await p.evaluate(() => {
    const d = document.createElement('div'); d.id = '__ab';
    d.style.cssText = 'position:absolute;left:820px;top:0;width:402px;height:1400px;overflow:auto;background:#fff';
    document.body.appendChild(d); window.__abRoot = ReactDOM.createRoot(d);
    window.__abRoot.render(React.createElement(AdminBingo, { app: 'torta' }));
  });
  await p.waitForTimeout(1000);
  ok(await p.evaluate(() => !document.querySelector('#__ab [data-bingo-mode]') && !!document.querySelector('#__ab [data-bingo-admin-app="torta"]')), 'az admin-fülön nincs mód-váltó, a fül maga a Tortán');
  const tg = await p.evaluate(() => {
    const row = [...document.querySelectorAll('#__ab div')].find(d => d.children.length === 2 && /Megjelenítés a DNR központban/.test(d.textContent) && d.textContent.length < 90);
    if (!row) return false; row.children[1].click(); return true;
  });
  ok(tg, 'a „Megjelenítés a DNR központban" kapcsolót átbillentjük (Mentés NÉLKÜL)');
  await p.waitForTimeout(700);
  const st = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(st.apps && st.apps.torta === false && st.apps.tipp === true && st.apps.bingo === true, '⚠️ csak a Tortán ment ki, a másik kettő marad', JSON.stringify(st.apps));
  ok((await card(p, 'torta')) === null && !!(await card(p, 'tipp')) && !!(await card(p, 'bingo')), '⚠️ a központból CSAK a Tortán csempe tűnt el');
  ok(st.mode === 'torta' && st.enabled === true, 'a többi mező érintetlen (merge)');

  console.log('\n===== 6b. RÉGI CONFIG + ADMIN-KAPCSOLÓ =====');
  await setDoc(p, 'bingoConfig', { enabled: true, mode: 'torta', tortaTitle: 'DNR a tortán' });
  await p.evaluate(() => window.__abRoot.render(React.createElement(AdminBingo, { key: 'b' + Math.random(), app: 'bingo' })));
  await p.waitForTimeout(900);
  await p.evaluate(() => {
    const row = [...document.querySelectorAll('#__ab div')].find(d => d.children.length === 2 && /Megjelenítés a DNR központban/.test(d.textContent) && d.textContent.length < 90);
    row && row.children[1].click();
  });
  await p.waitForTimeout(700);
  const st2 = await p.evaluate(() => window.__fbStore.config.bingoConfig.apps);
  ok(st2 && st2.bingo === true && st2.torta === true && st2.tipp === false, '⚠️ a Bingó bekapcsolása a régi configon a Tortánt NEM rejti el (a térkép materializálva megy ki)', JSON.stringify(st2));

  console.log('\n===== 7. SIKERTELEN MENTÉS NEM ÍR „MENTVE"-T =====');
  await p.evaluate(() => window.__abRoot.render(React.createElement(AdminBingo, { key: 't' + Math.random(), app: 'torta' })));
  await p.waitForTimeout(900);
  await p.evaluate(() => { window.setBingoConfig = () => Promise.reject({ code: 'permission-denied' }); });
  await p.evaluate(() => { const i = [...document.querySelectorAll('#__ab input')].find(x => x.value === 'DNR a tortán'); const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; set.call(i, 'DNR a tortán 2'); i.dispatchEvent(new Event('input', { bubbles: true })); });
  await p.waitForTimeout(200);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__ab button')].find(x => x.textContent.trim() === 'Mentés'); b && b.click(); });
  await p.waitForTimeout(400);
  const se = await p.evaluate(() => ({ err: (document.querySelector('#__ab [data-bingo-saveerr]') || {}).textContent || '', ok: /Mentve ✓/.test(document.getElementById('__ab').textContent) }));
  ok(/Nem sikerült menteni/.test(se.err) && /permission-denied/.test(se.err) && !se.ok, '⚠️ hibás írásnál hibaüzenet, NEM „Mentve ✓"', JSON.stringify(se));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
