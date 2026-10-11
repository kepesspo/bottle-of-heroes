// v10.402 — DNR a tortán a főképernyőn: ikon + a beállítás-kapcsoló
// v10.409 óta a „főképernyő" a DNR KÖZPONT (DnrHubScreen): a Bingó-gomb és a
// „DNR appok" lap ott egy csempe lett — a fogódzók ezért a központ csempéjét nézik.
//
// Bejelentés: „Nem a DNR a tortán ikon jelenik meg. Illetve ha beállításokba kinyomom,
// hogy ne látszódjon, akkor is megjelenik."
//
// Fogódzók (bingoConfig.mode = 'torta'):
//  1) a főképernyő gombja a torta-logót viszi
//  2) a „DNR appok" lapon a Bingó sor a torta-logóval és a „DNR a tortán" névvel áll
//  3) az admin beállítás („Melyik app látszódjon") sora is a torta-logót mutatja
//  4) ⚠️ homeConfig.dnrApps.bingo = false → a főképernyő gombja ELTŰNIK (eddig maradt)
//  5) a mód el van téve a nyitóképernyőnek (localStorage boh_bingo_mode = 'torta')
//  6) kontroll: bingo módban a lapon a régi Bingó ikon és név áll
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const TORTA = 'assets/dnr_torta_logo.png', BINGO = 'assets/dnr_bingo_icon.png';

const homeBtn = p => p.evaluate(() => {
  // v10.411: csak Kártya nézet — a kártya viszi az ikont és a nevet, a gomb csak „Megnyitás"
  const b = document.querySelector('#__h [data-hub-card="bingo"]');
  if (!b) return null;
  const i = b.querySelector('img'); return { txt: (b.textContent || '').trim(), src: i ? i.getAttribute('src') : null };
});
const sheetRow = (p, sel) => p.evaluate(sel => {
  const imgs = [...document.querySelectorAll(sel + ' img')];
  // a főképernyő nagy gombja (🏆) NEM a lap sora — azt kihagyjuk
  const i = imgs.find(x => /dnr_torta_logo|dnr_bingo_icon/.test(x.getAttribute('src') || '') && !/🏆/.test(((x.closest('button') || {}).textContent) || ''));
  if (!i) return null;
  const row = i.closest('button') || i.parentElement;
  return { src: i.getAttribute('src'), txt: (row.textContent || '').trim() };
}, sel);
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

  console.log('\n===== 1–2. A KÖZPONT CSEMPÉJE =====');
  const hb = await homeBtn(p);
  ok(hb && hb.src === TORTA, '⚠️ a központ Bingó-csempéje a torta-logót viszi', JSON.stringify(hb));
  ok(hb && /DNR a tortán/.test(hb.txt) && !/DNR Bingó/.test(hb.txt), 'a csempe neve a TELJES „DNR a tortán" (nem csonka „a tortán")', hb && hb.txt);

  console.log('\n===== 3. ADMIN BEÁLLÍTÁS SORA =====');
  const srow = await sheetRow(p, '#__s');
  ok(srow && srow.src === TORTA && /DNR a tortán/.test(srow.txt), '⚠️ a „Melyik app látszódjon" sorban is a torta-logó és név', JSON.stringify(srow));

  console.log('\n===== 4. KIKAPCSOLVA ELTŰNIK A FŐKÉPERNYŐRŐL =====');
  await setDoc(p, 'homeConfig', { dnrAppsEnabled: true, dnrApps: { bingo: false } });
  await p.waitForTimeout(600);
  ok((await homeBtn(p)) === null, '⚠️ dnrApps.bingo=false → a központ csempéje eltűnt', JSON.stringify(await homeBtn(p)));
  await setDoc(p, 'homeConfig', { dnrAppsEnabled: true, dnrApps: { bingo: true } });
  await p.waitForTimeout(600);
  ok(!!(await homeBtn(p)), 'visszakapcsolva újra ott a csempe (kontroll)');

  console.log('\n===== 5. NYITÓKÉPERNYŐ-EMLÉKEZET =====');
  ok((await p.evaluate(() => localStorage.getItem('boh_bingo_mode'))) === 'torta', 'boh_bingo_mode = torta');

  console.log('\n===== 6. KONTROLL: BINGÓ MÓD =====');
  await setDoc(p, 'bingoConfig', { enabled: true, mode: 'bingo' });
  await p.waitForTimeout(600);
  const row2 = await sheetRow(p, '#__s');
  ok(row2 && row2.src === BINGO && /DNR Bingó/.test(row2.txt), 'bingó módban a régi ikon és név', JSON.stringify(row2));
  ok((await p.evaluate(() => localStorage.getItem('boh_bingo_mode'))) === 'bingo', 'a mód-emlékezet követi (bingo)');

  console.log('\n===== 7. ADMIN → BINGÓ: A KAPCSOLÓ AZONNAL REJT (v10.405) =====');
  await setDoc(p, 'bingoConfig', { enabled: true, mode: 'torta', tortaTitle: 'DNR a tortán' });
  await setDoc(p, 'homeConfig', { dnrAppsEnabled: true });
  await p.evaluate(() => {
    const d = document.createElement('div'); d.id = '__ab';
    d.style.cssText = 'position:absolute;left:820px;top:0;width:402px;height:1400px;overflow:auto;background:#fff';
    document.body.appendChild(d); window.__abRoot = ReactDOM.createRoot(d);
    window.__abRoot.render(React.createElement(AdminBingo));
  });
  await p.waitForTimeout(1000);
  ok(!!(await homeBtn(p)), 'kiinduláskor ott a központ csempéje');
  const tg = await p.evaluate(() => {
    const row = [...document.querySelectorAll('#__ab div')].find(d => d.children.length === 2 && /Megjelenítés a főképernyőn/.test(d.textContent) && d.textContent.length < 90);
    if (!row) return false; row.children[1].click(); return true;
  });
  ok(tg, 'a „Megjelenítés a főképernyőn" kapcsolót átbillentjük (Mentés NÉLKÜL)');
  await p.waitForTimeout(700);
  ok((await p.evaluate(() => window.__fbStore.config.bingoConfig.enabled)) === false, '⚠️ a kapcsoló azonnal kiírta: enabled=false');
  ok((await homeBtn(p)) === null, '⚠️ a központ csempéje eltűnt — Mentés nélkül is');
  ok((await p.evaluate(() => window.__fbStore.config.bingoConfig.mode)) === 'torta', 'a többi mező érintetlen (merge)');

  console.log('\n===== 8. SIKERTELEN MENTÉS NEM ÍR „MENTVE"-T =====');
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
