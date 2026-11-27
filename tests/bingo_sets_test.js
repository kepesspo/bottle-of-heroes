// v10.473 — DNR Bingó: szettek (Foci VB / OTP Gála), korty-érték tételenként, kör-alapú jelölés,
// rugalmas kártyaméret (24+ → 5×5, 16–23 → 4×4), korty-összesítő + teli kártya.
//
// Fogódzók:
//  1) admin: a szettváltás elmenti a régit, betölti az OTP Gálát (18 szó, korty-értékkel) és ÚJ KÖRT indít
//  2) ⚠️ a régi jelölések NEM csúsznak át az új szett tételeire (kör-alapú tároló)
//  3) 18 tétel → 4×4-es kártya, nincs ingyen mező; minden mezőn a korty-jelvény
//  4) a saját sávban és az Állásban a korty = a megjelölt tételek `k`-összege
//  5) teli kártya → „TELI KÁRTYA” ünneplés és TELI jelölés az Állásban
//  6) kevés (16 alatti) tétel → üzenet, NEM csendes foci-lista
//  7) régi config (kör nélkül) → a régi jelölések élnek, 5×5, DÖNTŐ középen, ⚽ a címben
//  8) admin: a korty-gomb 1 → 2 → 3 → 1 körbe lép, és elmentődik
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const PROFILES = [{ id:'p0', name:'Sere', color:'#E07A5F' }, { id:'p1', name:'Kecsi', color:'#4FC2A0' }];

async function open(b, q, config, extraLs) {
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(({ config, profiles, extraLs }) => {
    try { localStorage.setItem('boh_onboarded', '1'); localStorage.setItem('boh_splash', '0'); Object.keys(extraLs || {}).forEach(k => localStorage.setItem(k, extraLs[k])); } catch(e) {}
    window.__fbStore['config'] = Object.assign(window.__fbStore['config'] || {}, config || {});
    const ps = {}; profiles.forEach(x => { ps[x.id] = x; });
    window.__fbStore['profiles'] = Object.assign(window.__fbStore['profiles'] || {}, ps);
  }, { config, profiles: PROFILES, extraLs: extraLs || {} });
  await p.goto('file://' + ROOT + '/index.html' + q, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);
  return p;
}
const txt = p => p.evaluate(() => (document.getElementById('root').innerText || '').replace(/\s+/g, ' '));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  console.log('\n===== 1. ADMIN: SZETTVÁLTÁS FOCI → OTP GÁLA =====');
  // régi config: kör nélkül, foci-lista, régi jelölések a felső szinten
  const LEGACY = { bingoConfig: { enabled: true, mode: 'bingo', apps: { bingo: true }, title: 'VB Bingó', items: [] }, bingo: { p0: [0, 1] } };
  let p = await open(b, '', LEGACY);
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const d = document.createElement('div'); d.id = '__ab'; document.body.appendChild(d);
    ReactDOM.createRoot(d).render(React.createElement(AdminBingo, { app: 'bingo' }));
  });
  await p.waitForTimeout(800);
  const chips = await p.evaluate(() => [...document.querySelectorAll('#__ab [data-bingo-set]')].map(x => x.getAttribute('data-bingo-set') + ':' + x.getAttribute('aria-pressed')));
  ok(JSON.stringify(chips) === '["foci:true","otp:false"]', 'két szett: Foci VB (aktív) és OTP Gála', JSON.stringify(chips));
  await p.click('#__ab [data-bingo-set="otp"]'); await p.waitForTimeout(200);
  await p.locator('button:text-is("Váltás")').click(); await p.waitForTimeout(600);
  let bc = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(bc.bingoSetId === 'otp' && bc.title === 'OTP Gála Bingó' && bc.items.length === 24 && !!bc.bingoRound && bc.center.t === 'OTP Gála 2027', 'az OTP Gála aktív: 24 tétel, középen „OTP Gála 2027”, új kör', JSON.stringify({ id: bc.bingoSetId, t: bc.title, n: bc.items.length, r: bc.bingoRound }));
  const rev = bc.items.find(x => x.t === 'Revolut'), dig = bc.items.find(x => x.t === 'Digitális bankolás');
  ok(rev && rev.k === 3 && dig && dig.k === 1, 'a korty-értékek a küldött táblázat szerint (Revolut 3, Digitális bankolás 1)');
  ok(bc.bingoSets && bc.bingoSets.foci && bc.bingoSets.foci.items.length === 24, 'a foci-szett elmentődött (24 tétel)');
  ok(/24 sorsolt mező/.test(await p.evaluate(() => document.querySelector('#__ab [data-bingo-gridnote]').textContent)), 'az admin kiírja: 24 tétel → 5×5-ös kártya');
  // korty-gomb körbe lép
  await p.click('#__ab [data-bingo-item-k="0"]'); await p.click('#__ab [data-bingo-item-k="0"]'); await p.click('#__ab [data-bingo-item-k="0"]');
  const kAfter3 = await p.evaluate(() => document.querySelector('#__ab [data-bingo-item-k="0"]').textContent);
  ok(kAfter3 === '🍺1', 'a korty-gomb 1 → 2 → 3 → 1 körbe lép', kAfter3);
  await p.click('#__ab [data-bingo-item-k="0"]');
  await p.evaluate(() => { const bt = [...document.querySelectorAll('#__ab button')].find(x => /^Mentés/.test(x.textContent.trim())); bt && bt.click(); });
  await p.waitForTimeout(500);
  bc = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(bc.items[0].k === 2 && bc.bingoSets.otp.items[0].k === 2, 'a módosított korty elmentődik (a szett másolatába is)', bc.items[0].k);
  // vissza focira: az OTP szerkesztés megmarad a szettben
  await p.click('#__ab [data-bingo-set="foci"]'); await p.waitForTimeout(200);
  await p.locator('button:text-is("Váltás")').click(); await p.waitForTimeout(500);
  bc = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(bc.bingoSetId === 'foci' && bc.items.length === 24 && bc.bingoSets.otp.items[0].k === 2, 'visszaváltva a foci jön, az OTP-szerkesztés megmarad');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  const store = await p.evaluate(() => JSON.parse(JSON.stringify(window.__fbStore.config)));
  await p.close();

  console.log('\n===== 2–5. 18 TÉTELES SZETT A KÉPERNYŐN (4×4) =====');
  const OTP = { enabled: true, mode: 'bingo', apps: { bingo: true }, bingoSetId: 'otp', bingoRound: 'r1', title: 'OTP Gála Bingó', titleEmoji: '🎤', center: { e:'🎤', t:'GÁLA' } };
  p = await open(b, '?screen=bingo', { bingoConfig: Object.assign({}, OTP, { items: await (async () => { const q = await b.newPage(); await q.goto('file://' + ROOT + '/index.html', { waitUntil:'domcontentloaded' }).catch(() => {}); await q.waitForTimeout(2500); const it = await q.evaluate(() => BINGO_PRESETS.otp.items.slice(0, 18)); await q.close(); return it; })() }), bingo: { p0: [0, 1, 2] } }, { boh_bingo_who: 'p0' });
  let t = await txt(p);
  ok(/OTP Gála Bingó 🎤/.test(t), 'a cím a szettből: „OTP Gála Bingó 🎤”');
  ok((await p.evaluate(() => document.querySelector('[data-bingo-grid]').getAttribute('data-bingo-grid'))) === '4' && (await p.evaluate(() => document.querySelectorAll('[data-bingo]').length)) === 16, '18 tétel → 4×4-es kártya, 16 mező');
  ok(!/GÁLA/.test(t), '4×4-en nincs ingyen mező');
  ok((await p.evaluate(() => document.querySelectorAll('[data-bingo-k]').length)) === 16, 'minden mezőn korty-jelvény');
  ok(/0\/16 kipipálva/.test(t), '⚠️ a régi (kör előtti) jelölések nem csúsznak át — tiszta kártya', (t.match(/\d+\/16 kipipálva/) || [''])[0]);
  // jelölés: a korty a megjelölt mezők k-összege
  const ks = await p.evaluate(() => [0, 1, 2].map(i => +document.querySelector(`[data-bingo="${i}"] [data-bingo-k]`).getAttribute('data-bingo-k')));
  for (const i of [0, 1, 2]) { await p.click(`[data-bingo="${i}"]`); await p.waitForTimeout(80); }
  await p.waitForTimeout(300);
  const want = ks.reduce((a, c) => a + c, 0);
  ok(+(await p.textContent('[data-bingo-mysips]')) === want, 'a saját korty = a megjelölt tételek összege', want);
  ok(+((await p.textContent('[data-bingo-row="p0"] [data-bingo-sips]')).replace(/\D/g, '')) === want, 'az Állás is ugyanezt mutatja');
  const st = await p.evaluate(() => window.__fbStore.config.bingo);
  ok(st.r_r1 && st.r_r1.p0 && st.r_r1.p0.length === 3 && JSON.stringify(st.p0) === '[0,1,2]', 'a jelölés a kör alá kerül (r_r1), a régi érintetlen', JSON.stringify(st.r_r1));
  // teli kártya
  // (egy kész sor után a „BINGÓ!” ablak feljön és eltakarja a rácsot — DOM-kattintással töltjük tovább)
  for (let i = 3; i < 16; i++) { await p.evaluate(i => document.querySelector(`[data-bingo="${i}"]`).click(), i); await p.waitForTimeout(60); }
  await p.waitForTimeout(500);
  ok((await p.evaluate(() => { const e = document.querySelector('[data-bingo-celebrate]'); return e && e.getAttribute('data-bingo-celebrate'); })) === 'full', 'teli kártya → „TELI KÁRTYA” ünneplés');
  ok(/TELI 🎉/.test(await txt(p)), 'az Állásban TELI jelölés');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 5b. OTP GÁLA 2027: 24 SZÓ → 5×5, KÖZÉPEN A FELIRAT =====');
  p = await open(b, '?screen=bingo', {}, {});
  const preset = await p.evaluate(() => BINGO_PRESETS.otp);
  await p.close();
  p = await open(b, '?screen=bingo', { bingoConfig: Object.assign({}, OTP, { center: preset.center, items: preset.items }) }, { boh_bingo_who: 'p0' });
  ok(preset.items.length === 24 && preset.items.slice(0, 18).map(x => x.t).join('|').includes('Revolut'), 'a preset: a tavalyi 18 + 6 új = 24 szó', preset.items.length);
  ok((await p.evaluate(() => document.querySelector('[data-bingo-grid]').getAttribute('data-bingo-grid'))) === '5' && /OTP Gála 2027/.test(await txt(p)), '5×5-ös kártya, középen „OTP Gála 2027”');
  ok((await p.evaluate(() => document.querySelectorAll('[data-bingo-k]').length)) === 24, '24 korty-jelvény (az ingyen közép nélkül)');
  await p.close();

  console.log('\n===== 5c. ⚠️ A RÉGI (18 SZAVAS) MENTETT MÁSOLAT HELYETT A FRISS PRESET =====');
  const OLD18 = preset.items.slice(0, 18);
  p = await open(b, '', { bingoConfig: { enabled: true, mode: 'bingo', apps: { bingo: true }, bingoSetId: 'foci', bingoRound: 'x', title: 'VB Bingó', items: [], bingoSets: { otp: { name: 'OTP Gála', title: 'OTP Gála Bingó', center: { e:'🎤', t:'GÁLA' }, items: OLD18 } } } });
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const d = document.createElement('div'); d.id = '__ab'; document.body.appendChild(d);
    ReactDOM.createRoot(d).render(React.createElement(AdminBingo, { app: 'bingo' }));
  });
  await p.waitForTimeout(800);
  await p.click('#__ab [data-bingo-set="otp"]'); await p.waitForTimeout(200);
  await p.locator('button:text-is("Váltás")').click(); await p.waitForTimeout(600);
  bc = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(bc.items.length === 24 && bc.center.t === 'OTP Gála 2027' && bc.bingoSets.otp.pv === 2, 'a régi verziós másolat helyett a 24 szavas preset jön (pv:2)', JSON.stringify({ n: bc.items.length, c: bc.center.t, pv: bc.bingoSets.otp.pv }));
  // kézi visszatöltés: elrontjuk, majd „Alap lista visszatöltése" + Mentés
  await p.evaluate(() => document.querySelector('#__ab [data-bingo-item-k="0"]').click());
  await p.click('#__ab [data-bingo-preset]'); await p.waitForTimeout(100);
  await p.evaluate(() => { const bt = [...document.querySelectorAll('#__ab button')].find(x => /^Mentés/.test(x.textContent.trim())); bt && bt.click(); });
  await p.waitForTimeout(500);
  bc = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(bc.items[0].k === preset.items[0].k && bc.items.length === 24, 'az „Alap lista visszatöltése” az eredeti listát hozza vissza');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 6. KEVÉS TÉTEL =====');
  p = await open(b, '?screen=bingo', { bingoConfig: Object.assign({}, OTP, { items: Array.from({ length: 10 }, (_, i) => ({ e:'⭐', t:'Szó ' + i, k:1 })) }) }, { boh_bingo_who: 'p0' });
  ok(!!(await p.$('[data-bingo-toofew]')) && !(await p.$('[data-bingo-grid]')), '10 tételnél üzenet, nem csendes foci-lista');
  await p.close();

  console.log('\n===== 7. RÉGI CONFIG (KÖR NÉLKÜL) =====');
  p = await open(b, '?screen=bingo', LEGACY, { boh_bingo_who: 'p0' });
  t = await txt(p);
  ok(/VB Bingó ⚽/.test(t) && /DÖNTŐ/.test(t) && (await p.evaluate(() => document.querySelector('[data-bingo-grid]').getAttribute('data-bingo-grid'))) === '5', 'régi config: VB Bingó ⚽, 5×5, DÖNTŐ középen');
  ok(/2\/24 kipipálva/.test(t), 'a régi jelölések megmaradnak (2/24)');
  await p.close();

  await b.close();
  console.log(fail ? `\n${fail} HIBA` : '\nMINDEN OK');
  process.exit(fail ? 1 : 0);
})();
