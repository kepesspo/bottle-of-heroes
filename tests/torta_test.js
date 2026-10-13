// v10.400 — DNR a tortán: a DNR Bingó 3. módja (főzős-vendéglátós pontozás)
//
// Fogódzók (6 profil, 3 csapat: A=p0+p1, B=p2+p3, C=p4+p5; 1 alkalom: A a házigazda, B+C vendég):
//  1) vendégként (p2) megjelenik az alkalom pontozó kártyája, 5 kategória × 1–10
//  2) a pontok a config/tortaScores.<alkalom>.<profil>-ba mennek; összeg 40/50, „Értékelés kész"
//  3) ugyanarra az értékre koppintva törlődik (visszavonás)
//  4) a ranglista ÉS az alkalom-összeg élőben frissül (A = 40, „40 / 200")
//  5) a házigazda (p0) NEM kap pontozó kártyát (a saját estéjét nem pontozza), de a ranglistát látja
//  6) lezárt alkalomnál a gombok tiltva, a koppintás nem ír
//  7) kódvédelemnél a kód-kártya megjelenik, pontozni nem lehet
//  8) a Tipp mód kódvédelme a közös renderGate-tel is működik (regresszió)
//  9) admin: a Tortán mód szerkesztője ment (csapat auto-névvel „Sere & Kecsi")
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PROFILES = [
  { id:'p0', name:'Sere',  color:'#E07A5F' }, { id:'p1', name:'Kecsi', color:'#4FC2A0' },
  { id:'p2', name:'Vivi',  color:'#A78BFA' }, { id:'p3', name:'Robi',  color:'#5BA0DB' },
  { id:'p4', name:'Luca',  color:'#F4C95A' }, { id:'p5', name:'Béla',  color:'#98A2B3' },
];
const CFG = {
  enabled: true, mode: 'torta', tortaTitle: 'DNR a tortán', tippRequireCode: false,
  tortaTeams: [
    { id:'tA', name:'Csapat A', members:['p0','p1'] },
    { id:'tB', name:'Csapat B', members:['p2','p3'] },
    { id:'tC', name:'Csapat C', members:['p4','p5'] },
  ],
  tortaEvenings: [ { id:'e1', date:'2026-10-10T19:00', hostId:'tA', guestIds:['tB','tC'], locked:false } ],
};

const scoreOf = (p, ev, pid) => p.evaluate(({ ev, pid }) => (((window.__fbStore['config'] || {}).tortaScores || {})[ev] || {})[pid] || null, { ev, pid });
const txt = p => p.evaluate(() => (document.getElementById('__b').innerText || '').replace(/\s+/g, ' '));
const tap = (p, ev, cat, n) => p.evaluate(({ ev, cat, n }) => { const b = document.querySelector(`[data-torta-ev="${ev}"] [data-torta-cat="${cat}"] [data-torta-val="${n}"]`); if (!b) return 'nincs'; if (b.disabled) return 'tiltva'; b.click(); return 'ok'; }, { ev, cat, n });
// v10.419: a Tortán és a Tipp KÜLÖN app — az `app` prop adja a módot, és a „Ki vagy?" apponként mentődik
const mountAs = (p, who, app = 'torta') => p.evaluate(({ who, app }) => {
  try { localStorage.setItem(app === 'bingo' ? 'boh_bingo_who' : 'boh_' + app + '_who', who || ''); } catch(e) {}
  window.__bRoot.render(React.createElement(BingoScreen, { key: 'k' + who + Math.random(), go: () => {}, deepLink: true, app }));
}, { who, app });
const setCfg = (p, patch) => p.evaluate(patch => firebase.firestore().collection('config').doc('bingoConfig').set(patch, { merge: true }), patch);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 2400 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ profiles, cfg }) => {
    window.__fbStore['config'] = Object.assign(window.__fbStore['config'] || {}, { bingoConfig: JSON.parse(JSON.stringify(cfg)) });
    window.getProfiles = () => Promise.resolve(profiles);
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const d = document.createElement('div'); d.id = '__b';
    d.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:2400px;overflow:auto;z-index:9;background:#fff;display:flex;flex-direction:column';
    document.body.appendChild(d);
    window.__bRoot = ReactDOM.createRoot(d);
  }, { profiles: PROFILES, cfg: CFG });

  // ── 1. Vendégként (Vivi, B csapat) a pontozó kártya ──
  console.log('\n===== 1. VENDÉG PONTOZÓ KÁRTYA =====');
  await mountAs(p, 'p2'); await p.waitForTimeout(900);
  const card = await p.evaluate(() => { const c = document.querySelector('[data-torta-ev="e1"]'); return c ? { cats: c.querySelectorAll('[data-torta-cat]').length, vals: c.querySelectorAll('[data-torta-val]').length, txt: c.innerText.replace(/\s+/g,' ') } : null; });
  ok(!!card, 'megvan az alkalom pontozó kártyája a vendégnek');
  ok(card && card.cats === 5 && card.vals === 50, '5 kategória × 10 érték', card && (card.cats + '×' + card.vals / Math.max(1, card.cats)));
  ok(card && /Csapat A/.test(card.txt) && /HÁZIGAZDA/i.test(card.txt), 'a házigazda (Csapat A) látszik', card && card.txt.slice(0, 80));
  const logo = await p.evaluate(() => { const i = document.querySelector('#__b img[data-torta-logo]'); return i ? { src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0 } : null; });
  ok(logo && logo.src === 'assets/dnr_torta_mark.png' && logo.ok, 'a DNR a tortán jele betöltődik (v10.423 óta az egységes ikoncsaládból)', JSON.stringify(logo));

  // ── 2. Pontozás → store + összeg ──
  console.log('\n===== 2. PONTOZÁS =====');
  const plan = { etel: 8, kreativ: 7, vendeg: 9, elmeny: 6, ossz: 10 };
  for (const [k, v] of Object.entries(plan)) { ok((await tap(p, 'e1', k, v)) === 'ok', `${k} = ${v}`); await p.waitForTimeout(120); }
  await p.waitForTimeout(300);
  const s1 = await scoreOf(p, 'e1', 'p2');
  ok(s1 && s1.etel === 8 && s1.kreativ === 7 && s1.vendeg === 9 && s1.elmeny === 6 && s1.ossz === 10, '⚠️ a store-ban a helyes értékelés (config/tortaScores.e1.p2)', JSON.stringify(s1));
  const t2 = await txt(p);
  ok(/40 \/ 50 pont/.test(t2) && /Értékelés kész/.test(t2), 'a kártya összege 40/50, „Értékelés kész"');

  // ── 3. Ugyanarra koppintva törlődik ──
  console.log('\n===== 3. VISSZAVONÁS =====');
  await tap(p, 'e1', 'etel', 8); await p.waitForTimeout(300);
  ok((await scoreOf(p, 'e1', 'p2')).etel == null, 'az ételek pontja törlődött', JSON.stringify(await scoreOf(p, 'e1', 'p2')));
  ok(/32 \/ 50 pont/.test(await txt(p)) && /4\/5 kategória/.test(await txt(p)), 'az összeg 32, „4/5 kategória"');
  await tap(p, 'e1', 'etel', 8); await p.waitForTimeout(300);

  // ── 4. Ranglista + alkalom-összeg élőben ──
  console.log('\n===== 4. RANGLISTA ÉLŐBEN =====');
  const rank = await p.evaluate(() => { const r = document.querySelector('[data-torta-team="tA"] [data-torta-pts]'); const e = document.querySelector('[data-torta-overview="e1"] [data-torta-evtotal]'); return { a: r ? r.textContent : null, ev: e ? e.textContent.replace(/\s+/g,' ') : null }; });
  ok(rank.a === '40', '⚠️ a ranglistán Csapat A = 40 pont', rank.a);
  ok(rank.ev === '40 / 200', 'az alkalom összege „40 / 200"', rank.ev);
  // egy második vendég (Luca, C) is pontoz → összeadódik
  await mountAs(p, 'p4'); await p.waitForTimeout(700);
  for (const k of ['etel','kreativ','vendeg','elmeny','ossz']) { await tap(p, 'e1', k, 10); await p.waitForTimeout(80); }
  await p.waitForTimeout(300);
  const rank2 = await p.evaluate(() => { const r = document.querySelector('[data-torta-team="tA"] [data-torta-pts]'); const e = document.querySelector('[data-torta-overview="e1"]'); return { a: r ? r.textContent : null, ev: e ? e.innerText.replace(/\s+/g,' ') : '' }; });
  ok(rank2.a === '90', '⚠️ két vendég után Csapat A = 90 pont (40 + 50)', rank2.a);
  ok(/2\/4 értékelt/.test(rank2.ev), '„2/4 értékelt" az alkalom kártyáján', rank2.ev.slice(0, 90));

  // ── 5. A házigazda nem pontozhat ──
  console.log('\n===== 5. HÁZIGAZDA =====');
  await mountAs(p, 'p0'); await p.waitForTimeout(700);
  ok(!(await p.evaluate(() => !!document.querySelector('[data-torta-ev="e1"]'))), '⚠️ a házigazda (Sere) NEM kap pontozó kártyát a saját estéjére');
  ok(await p.evaluate(() => !!document.querySelector('[data-torta-rank]')), 'a házigazda is látja a ranglistát');

  // ── 6. Lezárt alkalom ──
  console.log('\n===== 6. LEZÁRT ALKALOM =====');
  await setCfg(p, { tortaEvenings: [ { ...CFG.tortaEvenings[0], locked: true } ] });
  await mountAs(p, 'p2'); await p.waitForTimeout(700);
  ok((await tap(p, 'e1', 'etel', 3)) === 'tiltva', '⚠️ lezárt alkalomnál a pontgombok tiltva');
  ok((await scoreOf(p, 'e1', 'p2')).etel === 8, 'a korábbi pont változatlan (8)');
  await setCfg(p, { tortaEvenings: CFG.tortaEvenings });

  // ── 6b. v10.417: csak az este időpontja UTÁN pontozható ──
  console.log('\n===== 6b. PONTOZÁS CSAK AZ IDŐPONT UTÁN =====');
  const fut = (() => { const d = new Date(Date.now() + 3 * 864e5); const z = n => String(n).padStart(2, '0'); return `${d.getFullYear()}-${z(d.getMonth() + 1)}-${z(d.getDate())}T19:00`; })();
  await setCfg(p, { tortaEvenings: [ { ...CFG.tortaEvenings[0], date: fut } ] });
  await mountAs(p, 'p2'); await p.waitForTimeout(700);
  ok((await tap(p, 'e1', 'etel', 3)) === 'tiltva', '⚠️ jövőbeli estére még NEM lehet pontozni');
  ok(await p.evaluate(() => !!document.querySelector('[data-torta-ev="e1"] [data-torta-notyet]')) && /este kezdetekor nyílik meg/.test(await txt(p)), 'a kártya kiírja, mikor nyílik a pontozás');
  ok((await scoreOf(p, 'e1', 'p2')).etel === 8, 'a pont nem változott (8)');
  await setCfg(p, { tortaEvenings: [ { ...CFG.tortaEvenings[0], date: '' } ] });
  await mountAs(p, 'p2'); await p.waitForTimeout(700);
  ok((await tap(p, 'e1', 'etel', 3)) === 'tiltva' && /időpontja még nincs beállítva/.test(await txt(p)), '⚠️ időpont nélküli estére (friss sorsolás) sem lehet pontozni');
  await setCfg(p, { tortaEvenings: CFG.tortaEvenings });
  await mountAs(p, 'p2'); await p.waitForTimeout(700);
  ok(await p.evaluate(() => document.querySelector('[data-torta-ev="e1"]').getAttribute('data-torta-open') === '1'), 'kontroll: a múltbeli estére újra pontozható');

  // ── 7. Kódvédelem ──
  console.log('\n===== 7. KÓDVÉDELEM =====');
  await setCfg(p, { tippRequireCode: true });
  await mountAs(p, 'p3'); await p.waitForTimeout(700);
  const t7 = await txt(p);
  ok(/Kód kell a szerkesztéshez/.test(t7) && /a pontozásodat/.test(t7), '⚠️ a kód-kártya megjelenik („…szerkeszteni a pontozásodat")');
  ok((await tap(p, 'e1', 'etel', 5)) === 'tiltva', 'kód nélkül a pontgombok tiltva');

  // ── 8. Tipp mód — a közös gate regresszió ──
  console.log('\n===== 8. TIPP MÓD (REGRESSZIÓ) =====');
  await setCfg(p, { matches: [] });
  await mountAs(p, 'p3', 'tipp'); await p.waitForTimeout(700);
  const t8 = await txt(p);
  ok(/Kód kell a szerkesztéshez/.test(t8) && /a tippjeidet/.test(t8), 'Tipp módban is a kód-kártya („…a tippjeidet")');
  ok(!(await p.evaluate(() => !!document.querySelector('[data-torta-rank]'))), 'Tipp módban nincs Tortán-ranglista');
  await setCfg(p, { tippRequireCode: false });

  // ── 8b. „Ki vagy?" — Tortán módban CSAK a csapattagok (v10.403) ──
  console.log('\n===== 8b. KI VAGY? — CSAK CSAPATTAGOK =====');
  await p.evaluate(profiles => { window.getProfiles = () => Promise.resolve(profiles.concat([{ id:'p6', name:'Kívülálló', color:'#333333' }])); }, PROFILES);
  await mountAs(p, ''); await p.waitForTimeout(800);
  const picks = await p.evaluate(() => [...document.querySelectorAll('[data-who-pick]')].map(b => b.getAttribute('data-who-pick')).sort());
  ok(picks.join() === 'p0,p1,p2,p3,p4,p5', '⚠️ a választóban csak a 6 csapattag áll (a csapaton kívüli p6 nem)', picks.join());
  // egy korábban elmentett, csapaton kívüli „who" visszakerül a választóra
  await mountAs(p, 'p6'); await p.waitForTimeout(800);
  ok(await p.evaluate(() => document.querySelectorAll('[data-who-pick]').length === 6), 'a csapaton kívüli elmentett játékos a választót kapja');
  // kontroll: Tipp módban mindenki választható
  await mountAs(p, '', 'tipp'); await p.waitForTimeout(700);
  ok(await p.evaluate(() => document.querySelectorAll('[data-who-pick]').length === 7), 'kontroll: Tipp módban mind a 7 profil választható');
  await p.evaluate(profiles => { window.getProfiles = () => Promise.resolve(profiles); }, PROFILES);

  // ── 9. Admin szerkesztő ──
  console.log('\n===== 9. ADMIN =====');
  await p.evaluate(() => { window.__bRoot.render(React.createElement(AdminBingo, { key: 'adm', app: 'torta' })); });
  await p.waitForTimeout(900);
  const adm = await p.evaluate(() => ({ modeBtn: !!document.querySelector('[data-bingo-admin-app="torta"]') && !document.querySelector('[data-bingo-mode]'), teams: document.querySelectorAll('[data-torta-admin-team]').length, evs: document.querySelectorAll('[data-torta-admin-ev]').length }));
  ok(adm.modeBtn && adm.teams === 3 && adm.evs === 1, 'az admin Tortán nézete: 3 csapat, 1 alkalom', JSON.stringify(adm));
  // új csapat: név nélkül, 2 taggal → mentéskor „Sere & Kecsi"-szerű auto-név
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__b button')].find(x => /Új csapat/.test(x.textContent)); b && b.click(); });
  await p.waitForTimeout(200);
  // a csapatok szabad profilok nélkül maradnak (mind a 6 foglalt) — ezért előbb kivesszük p4/p5-öt a C-ből
  await p.evaluate(() => {
    const setSel = (sel, v) => { const s = sel; const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set; setter.call(s, v); s.dispatchEvent(new Event('change', { bubbles: true })); };
    const c = document.querySelector('[data-torta-admin-team="2"]'); const sels = c.querySelectorAll('select'); setSel(sels[0], ''); setSel(sels[1], '');
  });
  await p.waitForTimeout(200);
  await p.evaluate(() => {
    const setSel = (s, v) => { const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set; setter.call(s, v); s.dispatchEvent(new Event('change', { bubbles: true })); };
    const c = document.querySelector('[data-torta-admin-team="3"]'); const sels = c.querySelectorAll('select'); setSel(sels[0], 'p4');
  });
  await p.waitForTimeout(150);
  await p.evaluate(() => {
    const setSel = (s, v) => { const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set; setter.call(s, v); s.dispatchEvent(new Event('change', { bubbles: true })); };
    const c = document.querySelector('[data-torta-admin-team="3"]'); const sels = c.querySelectorAll('select'); setSel(sels[1], 'p5');
  });
  await p.waitForTimeout(200);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__b button')].find(x => x.textContent.trim() === 'Mentés'); b && b.click(); });
  await p.waitForTimeout(600);
  const saved = await p.evaluate(() => (window.__fbStore['config'] || {}).bingoConfig || {});
  const newT = (saved.tortaTeams || []).find(t => (t.members || []).join() === 'p4,p5');
  ok(saved.mode === 'torta', 'mentés után a régi mód-mező érintetlen („torta")', saved.mode);
  ok(saved.apps && saved.apps.torta === true && saved.apps.bingo === false && saved.apps.tipp === false, 'mentéskor a láthatóság appokra bontva megy ki (régi szabályból materializálva)', JSON.stringify(saved.apps));
  ok(!!newT && newT.name === 'Luca & Béla', '⚠️ név nélküli csapat auto-nevet kap a tagokból („Luca & Béla")', newT && newT.name);
  ok((saved.tortaTeams || []).length === 3, 'a tag nélküli (kiürített) csapat kiesik mentéskor', (saved.tortaTeams || []).length);
  const ev1 = (saved.tortaEvenings || [])[0] || {};
  ok(ev1.hostId === 'tA' && JSON.stringify(ev1.guestIds) === JSON.stringify(['tB']), 'a törölt vendégcsapat (C) kiesik az alkalomból', JSON.stringify(ev1.guestIds));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
