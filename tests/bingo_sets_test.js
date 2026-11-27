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
  ok(bc.bingoSetId === 'otp' && bc.title === 'OTP Gála Bingó' && bc.items.length === 36 && !!bc.bingoRound && bc.center.t === 'OTP Gála 2027', 'az OTP Gála aktív: 36 tétel, középen „OTP Gála 2027”, új kör', JSON.stringify({ id: bc.bingoSetId, t: bc.title, n: bc.items.length, r: bc.bingoRound }));
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
  ok(preset.items.length === 36 && preset.items.slice(0, 18).map(x => x.t).join('|').includes('Revolut') && new Set(preset.items.map(x => x.t)).size === 36, 'a preset: a tavalyi 18 + 18 új = 36 különböző szó', preset.items.length);
  ok((await p.evaluate(() => document.querySelector('[data-bingo-grid]').getAttribute('data-bingo-grid'))) === '5' && /OTP Gála 2027/.test(await txt(p)), '5×5-ös kártya, középen „OTP Gála 2027”');
  ok((await p.evaluate(() => document.querySelectorAll('[data-bingo-k]').length)) === 24, '24 korty-jelvény (az ingyen közép nélkül)');
  // v10.478: 36 szóból mindenki SAJÁT 24-et kap — két játékos szókészlete eltér, egy kártyán nincs ismétlés
  const sets2 = await p.evaluate(() => ['p0', 'p1'].map(id => bingoCardFor(id, BINGO_PRESETS.otp.items.length).slice(0, 24)));
  const a0 = new Set(sets2[0]), a1 = new Set(sets2[1]), common = sets2[0].filter(x => a1.has(x)).length;
  ok(a0.size === 24 && a1.size === 24 && common < 24 && sets2[0].concat(sets2[1]).every(i => i >= 0 && i < 36), '⚠️ 36 szónál két játékos más-más 24-et kap (közös: ' + common + ')', common);
  const shown = await p.evaluate(() => [...document.querySelectorAll('[data-bingo]')].map(c => c.innerText.replace(/\s+/g, ' ').trim()));
  ok(new Set(shown).size === 25, 'a kártyán 25 különböző mező (nincs ismétlés)');
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
  ok(bc.items.length === 36 && bc.center.t === 'OTP Gála 2027' && bc.bingoSets.otp.pv === 3, 'a régi verziós másolat helyett a 36 szavas preset jön (pv:3)', JSON.stringify({ n: bc.items.length, c: bc.center.t, pv: bc.bingoSets.otp.pv }));
  // kézi visszatöltés: elrontjuk, majd „Alap lista visszatöltése" + Mentés
  await p.evaluate(() => document.querySelector('#__ab [data-bingo-item-k="0"]').click());
  await p.click('#__ab [data-bingo-preset]'); await p.waitForTimeout(100);
  await p.evaluate(() => { const bt = [...document.querySelectorAll('#__ab button')].find(x => /^Mentés/.test(x.textContent.trim())); bt && bt.click(); });
  await p.waitForTimeout(500);
  bc = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(bc.items[0].k === preset.items[0].k && bc.items.length === 36, 'az „Alap lista visszatöltése” az eredeti listát hozza vissza');
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

  console.log('\n===== 8. KÁRTYA-KINÉZET: NAGY SZÖVEG / KAPARÓS (v10.477) =====');
  // elválasztás: a magyar szótag-határon, a kétjegyű betű együtt marad
  const cuts = await (async () => { const q = await open(b, '', {}); const r = await q.evaluate(() => ({
    f: bingoHyphenCuts('Fenntarthatóság'), t: bingoHyphenCuts('transzformáció'), cs: bingoHyphenCuts('Csapatmunka') })); await q.close(); return r; })();
  ok(cuts.f.includes(8) && cuts.t.every(i => !(i === 5)) && cuts.t.includes(6), 'elválasztási pontok: „Fenntart|hatóság”, a „sz” nem vágódik ketté', JSON.stringify(cuts));
  for (const st of ['text', 'scratch']) {
    p = await open(b, '?screen=bingo', { bingoConfig: Object.assign({}, OTP, { center: preset.center, items: preset.items, bingoCardStyle: st }) }, { boh_bingo_who: 'p0' });
    const g = await p.evaluate(() => ({
      cells: document.querySelectorAll(`[data-bingo-cellstyle]`).length,
      k: document.querySelectorAll('[data-bingo-k]').length,
      reveal: document.querySelectorAll('[data-bingo-reveal]').length,
      emojiInCells: [...document.querySelectorAll('[data-bingo]')].some(c => /\p{Extended_Pictographic}/u.test(c.innerText)),
    }));
    ok(g.cells === 25 && g.k === 0 && g.reveal === 0, `${st}: 25 mező, a korty REJTETT kipipálás előtt`, JSON.stringify(g));
    ok(!g.emojiInCells, `${st}: nincs ikon a mezőkben`);
    // ⚠️ nincs kilógó / szó közepén tört szöveg: minden felirat befér a mezőbe, és a (nem elválasztott)
    // szavak egy sorban vannak
    const over = await p.evaluate(() => [...document.querySelectorAll('[data-bingo-cellstyle] > span')].filter(sp => {
      const c = sp.parentElement.getBoundingClientRect(), r = sp.getBoundingClientRect();
      return r.width > c.width - 4 || r.height > c.height - 4;
    }).map(sp => sp.textContent));
    ok(over.length === 0, `${st}: minden felirat befér a mezőbe`, JSON.stringify(over));
    const mid = await p.evaluate(() => [...document.querySelectorAll('[data-bingo-cellstyle] > span')].filter(sp => {
      // szavanként: ha a szó (elválasztás nélkül) két sorba esik, az a csúnya szótörés
      return sp.textContent.split(/\s+/).some(w => {
        if (w.indexOf('\u00AD') >= 0) return false;
        const rg = document.createRange(), i = sp.textContent.indexOf(w), tn = sp.firstChild;
        rg.setStart(tn, i); rg.setEnd(tn, i + w.length);
        return new Set([...rg.getClientRects()].map(r => Math.round(r.top))).size > 1;
      });
    }).map(sp => sp.textContent));
    ok(mid.length === 0, `${st}: egyetlen szó sem törik szét elválasztás nélkül`, JSON.stringify(mid));
    // kipipálás → kiderül a korty
    const target = await p.evaluate(() => { const c = [...document.querySelectorAll('[data-bingo]')].find(x => x.getAttribute('data-bingo') !== '12'); return c.getAttribute('data-bingo'); });
    await p.evaluate(c => document.querySelector(`[data-bingo="${c}"]`).click(), target); await p.waitForTimeout(500);
    const rv = await p.evaluate(c => { const el = document.querySelector(`[data-bingo="${c}"]`), r = el.querySelector('[data-bingo-reveal]');
      return { k: r && r.getAttribute('data-bingo-reveal'), txt: r && r.textContent, bg: getComputedStyle(el).backgroundColor, sips: document.querySelector('[data-bingo-mysips]').textContent }; }, target);
    const tone = { 1: 'rgb(46, 158, 118)', 2: 'rgb(232, 150, 30)', 3: 'rgb(224, 83, 63)' };
    ok(rv.k && rv.sips === rv.k && rv.txt.replace('+', '') === rv.k, `${st}: kipipálva megjelenik a korty (${rv.txt}), és ennyi kerül a saját sávba`, JSON.stringify(rv));
    if (st === 'scratch') ok(rv.bg === tone[rv.k], 'kaparós: a felfedett mező színe a tétet mutatja', rv.bg);
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }
  // kontroll: az ikonos (alap) változatlan — jelvény minden mezőn
  p = await open(b, '?screen=bingo', { bingoConfig: Object.assign({}, OTP, { center: preset.center, items: preset.items }) }, { boh_bingo_who: 'p0' });
  ok((await p.evaluate(() => document.querySelectorAll('[data-bingo-k]').length)) === 24 && (await p.evaluate(() => document.querySelectorAll('[data-bingo-cellstyle]').length)) === 0, 'kontroll: alapból az ikonos kártya, a korty látszik');
  await p.close();
  // admin: a kinézet-választó azonnal ment
  p = await open(b, '', { bingoConfig: { enabled: true, mode: 'bingo', apps: { bingo: true } } });
  await p.evaluate(() => { const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const d = document.createElement('div'); d.id = '__adm'; document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(AdminBingo, { app: 'bingo' })); });
  await p.waitForTimeout(800);
  await p.evaluate(() => document.querySelector('#__adm [data-bingo-style="scratch"]').click()); await p.waitForTimeout(400);
  ok(await p.evaluate(() => (window.__fbStore.config.bingoConfig || {}).bingoCardStyle) === 'scratch', 'admin: a kinézet-választó a bingoConfig.bingoCardStyle-t írja');
  await p.close();

  console.log('\n===== 9. BINGÓ = +N KORTY (ADMINBAN ÁLLÍTHATÓ) + ÚJ KÖR, HA A LISTA HOSSZA VÁLTOZIK (v10.478) =====');
  for (const [ls, label] of [[undefined, 'alap (hiányzó mező)'], [0, 'Nincs'], [2, '+2']]) {
    const cfgB = Object.assign({}, OTP, { center: preset.center, items: preset.items }, ls === undefined ? {} : { bingoLineSips: ls });
    p = await open(b, '?screen=bingo', { bingoConfig: cfgB }, { boh_bingo_who: 'p0' });
    // az első sor (0–4) teljes kipipálása → 1 BINGÓ
    const expK = await p.evaluate(() => { const cd = bingoCardFor('p0', BINGO_PRESETS.otp.items.length); return [0,1,2,3,4].reduce((t, c) => t + bingoK(BINGO_PRESETS.otp.items[cd[c]]), 0); });
    for (const c of [0, 1, 2, 3, 4]) { await p.evaluate(c => document.querySelector(`[data-bingo="${c}"]`).click(), c); await p.waitForTimeout(80); }
    await p.waitForTimeout(400);
    const r = await p.evaluate(() => ({ sips: +document.querySelector('[data-bingo-mysips]').textContent,
      btn: (document.querySelector('[data-bingo-celebrate-ok]') || {}).textContent, pop: !!document.querySelector('[data-bingo-celebrate="1"]') }));
    const n = ls === undefined ? 1 : ls;
    ok(r.pop && r.sips === expK + n, `${label}: BINGÓ után a korty = mezők (${expK}) + ${n}`, JSON.stringify(r));
    ok(n ? r.btn === '+' + n + ' korty 🍺' : /Fenékig/.test(r.btn), `${label}: a gomb felirata`, r.btn);
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }
  // admin: a BINGÓ-korty választó azonnal ment
  p = await open(b, '', { bingoConfig: { enabled: true, mode: 'bingo', apps: { bingo: true } } });
  await p.evaluate(() => { const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const d = document.createElement('div'); d.id = '__ab'; document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(AdminBingo, { app: 'bingo' })); });
  await p.waitForTimeout(800);
  ok(await p.evaluate(() => document.querySelector('#__ab [data-bingo-linesips="1"]').getAttribute('aria-pressed') === 'true'), 'admin: alapból +1');
  await p.evaluate(() => document.querySelector('#__ab [data-bingo-linesips="2"]').click()); await p.waitForTimeout(400);
  ok(await p.evaluate(() => window.__fbStore.config.bingoConfig.bingoLineSips) === 2, 'admin: a választó a bingoLineSips-et írja');
  await p.close();
  // ⚠️ a lista hossza változik (24 → 36) → a Mentés ÚJ KÖRT indít (a pipák különben más szavakra csúsznának)
  const OTP24 = Object.assign({}, OTP, { center: preset.center, items: preset.items.slice(0, 24), bingoRound: 'r24' });
  p = await open(b, '', { bingoConfig: OTP24 });
  await p.evaluate(() => { const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const d = document.createElement('div'); d.id = '__ab'; document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(AdminBingo, { app: 'bingo' })); });
  await p.waitForTimeout(800);
  const saveBtn = () => p.evaluate(() => { const bt = [...document.querySelectorAll('#__ab button')].find(x => x.textContent.trim() === 'Mentés'); bt && bt.click(); });
  // kontroll: azonos darabszám (egy korty-érték átírása) → a kör marad
  await p.evaluate(() => document.querySelector('#__ab [data-bingo-item-k="0"]').click()); await p.waitForTimeout(100);
  ok(!(await p.evaluate(() => !!document.querySelector('#__ab [data-bingo-newround-note]'))), 'azonos darabszámnál nincs új-kör figyelmeztetés');
  await saveBtn(); await p.waitForTimeout(500);
  ok(await p.evaluate(() => window.__fbStore.config.bingoConfig.bingoRound) === 'r24', 'kontroll: azonos darabszám → a kör marad (a pipák a helyükön)');
  await p.click('#__ab [data-bingo-preset]'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => /24 → 36/.test((document.querySelector('#__ab [data-bingo-newround-note]') || {}).textContent || '')), 'a visszatöltés után kiírja: 24 → 36, új kör jön');
  await saveBtn(); await p.waitForTimeout(500);
  const bcN = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(bcN.items.length === 36 && bcN.bingoRound && bcN.bingoRound !== 'r24', '⚠️ a hosszabb lista mentése új kört indít', JSON.stringify({ n: bcN.items.length, r: bcN.bingoRound }));
  ok(!(await p.evaluate(() => !!document.querySelector('#__ab [data-bingo-newround-note]'))), 'mentés után a figyelmeztetés eltűnik');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? `\n${fail} HIBA` : '\nMINDEN OK');
  process.exit(fail ? 1 : 0);
})();
