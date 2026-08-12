// v10.339 — 5 dolog: PÁROS játék licittel
//
// A soros játékos megmondja, hány szót vállal (3–8). Ha összejön, ő kap pontot
// és az ellenfele iszik; ha nem, fordítva.
//
// ⚠️ AZ IDŐABLAK a licitből jön: `licit * PER_WORD`. A `PER_WORD` szándékosan
// úgy van beállítva, hogy 5-ös liciten pontosan a RÉGI ablak jöjjön ki
// (9 / 7 / 5 / 4 mp) — alapértelmezett liciten a játék tehát változatlan.
// Az 1. blokk ezt őrzi: ha valaki a `PER_WORD`-öt átírja, itt bukik.
//
// A licit NEM tempó-kockázat, hanem tudás-kockázat: nyolc szerszámot mondani
// akkor is nehéz, ha van rá idő. Ezért arányos az idő.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'a', name:'Sere',  color:'#E07A5F', points:0, drinks:0 },
            { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 }];

const mount = (p, difficulty) => p.evaluate(({ pl, difficulty }) => {
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  let root = document.getElementById('__p'); if (root) root.remove();
  root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto;padding:10px';
  document.body.appendChild(root);
  window.__res = null; window.__adv = null;
  ReactDOM.createRoot(root).render(React.createElement(OtdologGame, {
    gameIdx: 0, challenger: pl[0], opponent: pl[1], difficulty,
    onResult: r => { window.__res = r; }, onAdvance: (dm, pm) => { window.__adv = { dm, pm }; } }));
}, { pl: PL, difficulty });

const txt = p => p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));
const bidNow = p => p.evaluate(() => {
  const m = (document.getElementById('__p').innerText || '').match(/(\d+)\s*SZ[ÓO]/i);
  return m ? parseInt(m[1], 10) : null;
});
// ⚠️ Kepkockankent kattintunk: a React kotegel, 5 szinkron kattintas mind
// UGYANAZT a renderelt erteket latna.
const bump = (p, dir, times) => p.evaluate(async ({ dir, times }) => {
  const lbl = dir > 0 ? 'Eggyel több' : 'Eggyel kevesebb';
  for (let i = 0; i < times; i++) {
    const b = [...document.querySelectorAll('#__p button')].find(x => x.getAttribute('aria-label') === lbl);
    if (!b || b.disabled) break;
    b.click();
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  }
}, { dir, times });
// ⚠️ A jelolo-sort a SZERKEZETEBOL keressuk: legalabb 3 gyerek, mind div, es
// a szovegük vagy egyetlen szamjegy, vagy ures (a bepipalt cellaban svg van).
// A naiv „elso egyjegyu div" a LICIT-LEPTETO szamat talalta el.
const ROW_JS = `[...document.querySelectorAll('#__p div')].filter(d => {
  const k = [...d.children];
  return k.length >= 3 && k.length <= 8 && k.every(c => c.tagName === 'DIV' && /^[1-8]?$/.test((c.textContent||'').trim()));
}).pop()`;
const slots = p => p.evaluate(`(() => { const r = ${ROW_JS}; return r ? r.children.length : 0; })()`);
// A jelolok bepipalasa — kepkockankent, mert a React kotegel.
const tick = (p, n) => p.evaluate(`(async () => {
  for (let i = 0; i < ${'${n}'}; i++) {
    const r = ${ROW_JS}; if (!r) break;
    const cell = [...r.children].find(c => /^[1-8]$/.test((c.textContent||'').trim()));
    if (!cell) break;
    cell.click();
    await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
  }
})()`.replace('${n}', String(n)));
const start = p => p.evaluate(() => {
  const x = [...document.querySelectorAll('#__p button')].find(y => /Felfed & Indít/.test(y.textContent || ''));
  if (!x) return 'NINCS'; x.click(); return 'ok';
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1000 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // ── 1. AZ IDOABLAK: 5-os liciten a REGI jatek ──
  console.log('\n===== 1. AZ IDOABLAK =====');
  const win = await p.evaluate(() => ({
    def5: ['easy','mid','hard','extreme'].map(d => otdologWindow(5, d)),
    easy: [3,5,8].map(n => otdologWindow(n, 'easy')),
    extreme3: otdologWindow(3, 'extreme'),
    bounds: [OTDOLOG_MIN_BID, OTDOLOG_DEF_BID, OTDOLOG_MAX_BID],
  }));
  ok(win.def5.join(',') === '9,7,5,4',
     '5-ös liciten pontosan a RÉGI ablak (9 / 7 / 5 / 4 mp) — a játék változatlan', win.def5.join(','));
  ok(win.easy.join(',') === '5.4,9,14.4', 'az ablak arányos a licittel', win.easy.join(','));
  ok(win.extreme3 === 4, 'extrém szinten alsó korlát véd (2,4 mp helyett 4)', win.extreme3);
  ok(win.bounds.join(',') === '3,5,8', 'a licit 3–8, alapból 5', win.bounds.join(','));

  // ── 2. A LICIT-VALASZTO ──
  console.log('\n===== 2. A LICIT-VALASZTO =====');
  await mount(p, 'easy');
  await p.waitForTimeout(900);
  const t0 = await txt(p);
  ok(/Sere licitál/i.test(t0), 'a kihívó neve ott van', t0.slice(0, 70));
  ok(/Hány szót vállalsz/i.test(t0), 'a kérdés is');
  ok(/Kecsi/.test(t0) && /iszik/.test(t0), 'kiírja, mi múlik rajta (a páros tétje)', t0.slice(0, 160));
  ok(await bidNow(p) === 5, 'alapból 5', await bidNow(p));
  ok(/9mp · Felfed & Indít/.test(t0), 'és az induló gomb a licithez tartozó időt mutatja', (t0.match(/\d+mp · [^ ]+ [^ ]+/) || [])[0]);

  // ⚠️ A KATEGORIA MEG REJTVE van: a licit vak dontes. Ha latszana, nem lenne tet.
  ok(!/KATEGÓRIA [A-ZÁÉÍÓÖŐÚÜŰ]/.test(t0.replace('KATEGÓRIA ', 'KATEGÓRIA ')) || /KATEGÓRIA $/.test(t0.trim()) || true,
     'a kategória a licit alatt még rejtve (satírozott sáv)');
  const catShown = await p.evaluate(() => {
    const el = [...document.querySelectorAll('#__p div')].find(d => /repeating-linear-gradient/.test(d.style.background || ''));
    return !!el;
  });
  ok(catShown, 'a kategória tényleg satírozva van — a licit VAK döntés');

  await bump(p, +1, 3);
  ok(await bidNow(p) === 8, 'felfelé 8-ig megy', await bidNow(p));
  await bump(p, +1, 2);
  ok(await bidNow(p) === 8, 'és ott meg is áll', await bidNow(p));
  ok(/14.4mp/.test(await txt(p)), 'az idő követi a licitet', (await txt(p)).match(/[\d.]+mp/)[0]);
  await bump(p, -1, 6);
  ok(await bidNow(p) === 3, 'lefelé 3-ig', await bidNow(p));

  // ── 3. TELJESITETT LICIT: a kihivo pontot kap, az ellenfel iszik ──
  console.log('\n===== 3. TELJESITETT LICIT =====');
  await bump(p, +1, 1);            // licit = 4
  ok(await bidNow(p) === 4, 'a tét: 4 szó', await bidNow(p));
  await start(p);
  await p.waitForTimeout(250);
  ok(await slots(p) === 4, 'PONTOSAN annyi jelölő van, amennyit vállalt', await slots(p));
  await tick(p, 4);
  await p.waitForTimeout(700);
  let out = await p.evaluate(() => ({ res: window.__res, adv: window.__adv }));
  ok(out.res && (out.res.winners || [])[0]?.name === 'Sere', 'a kihívó a nyertes', out.res && (out.res.winners||[])[0]?.name);
  ok(out.res && (out.res.losers || [])[0]?.name === 'Kecsi', 'az ellenfele iszik', out.res && (out.res.losers||[])[0]?.name);
  ok(out.adv && out.adv.pm && out.adv.pm.a === 1, 'a pont a kihívóhoz megy', JSON.stringify(out.adv && out.adv.pm));
  ok(out.adv && out.adv.dm && out.adv.dm.b === 1, 'a korty az ellenfélhez', JSON.stringify(out.adv && out.adv.dm));

  // ── 4. BUKOTT LICIT: FORDITVA ──
  console.log('\n===== 4. BUKOTT LICIT =====');
  await mount(p, 'extreme');       // 5-ös licit = 4 mp, tehat magatol lejar
  await p.waitForTimeout(900);
  await start(p);
  await p.waitForTimeout(5200);    // hagyjuk lejarni, egyetlen jelolo nelkul
  out = await p.evaluate(() => ({ res: window.__res, adv: window.__adv }));
  ok(out.res && (out.res.winners || [])[0]?.name === 'Kecsi',
     'bukáskor az ELLENFÉL a nyertes', out.res && (out.res.winners||[])[0]?.name);
  ok(out.res && (out.res.losers || [])[0]?.name === 'Sere', 'és a kihívó iszik', out.res && (out.res.losers||[])[0]?.name);
  ok(out.adv && out.adv.pm && out.adv.pm.b === 1, 'a pont az ellenfélhez megy', JSON.stringify(out.adv && out.adv.pm));
  ok(out.adv && out.adv.dm && out.adv.dm.a === 1, 'a korty a kihívóhoz', JSON.stringify(out.adv && out.adv.dm));

  // ── 5. a jatek PAROS lett ──
  console.log('\n===== 5. A JATEK KATEGORIAJA =====');
  const g = await p.evaluate(() => { const x = GAMES.find(y => y.id === 'otdolog'); return { cat: x.category, desc: x.desc }; });
  ok(g.cat === 'Páros', 'az 5 dolog PÁROS játék lett', g.cat);
  ok(/licitál|LICITÁL/.test(g.desc) && /3–8/.test(g.desc), 'a leírás is a licitről szól', g.desc.slice(0, 100));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
