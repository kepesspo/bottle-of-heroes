// v10.339 / v10.350 — 5 dolog: PÁROS játék licittel
//
// A soros játékos megmondja, hány szót vállal (legalább 3, FELSŐ HATÁR NINCS).
// Ha összejön, ő kap pontot és az ellenfele iszik; ha nem, fordítva.
//
// v10.350 négy dolgot fordított meg, és mind a négy külön blokkot kapott:
//   • a licitnek nincs plafonja (a jelölő-sor ezért RÁCS, nem egyetlen sor);
//   • ⚠️ a KATEGÓRIA már a licit alatt LÁTSZIK — a v10.339 szándékosan
//     satírozta („vak licit"), a tulajdonos döntése az ellenkező;
//   • az óra a közös `BohTimer` sávja, nem a 160 px-es gyűrű;
//   • ⚠️ a PlayScreen kézi „Vesztettem / Nyertem!" gombjai KIMARADNAK: a játék
//     maga könyvel, két egymásnak ellentmondó út vezetett a ponthoz.
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
  return k.length >= 3 && k.length <= 40 && k.every(c => c.tagName === 'DIV' && /^\\d{0,2}$/.test((c.textContent||'').trim()));
}).pop()`;
const slots = p => p.evaluate(`(() => { const r = ${ROW_JS}; return r ? r.children.length : 0; })()`);
// A jelolok bepipalasa — kepkockankent, mert a React kotegel.
const tick = (p, n) => p.evaluate(`(async () => {
  for (let i = 0; i < ${'${n}'}; i++) {
    const r = ${ROW_JS}; if (!r) break;
    const cell = [...r.children].find(c => /^\\d{1,2}$/.test((c.textContent||'').trim()));
    if (!cell) break;
    cell.click();
    await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
  }
})()`.replace('${n}', String(n)));
const start = p => p.evaluate(() => {
  const x = [...document.querySelectorAll('#__p button')].find(y => /Indítás/.test(y.textContent || ''));
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
    bounds: [OTDOLOG_MIN_BID, OTDOLOG_DEF_BID],
    noMax: typeof OTDOLOG_MAX_BID,
    big: otdologWindow(20, 'easy'),
  }));
  ok(win.def5.join(',') === '9,7,5,4',
     '5-ös liciten pontosan a RÉGI ablak (9 / 7 / 5 / 4 mp) — a játék változatlan', win.def5.join(','));
  ok(win.easy.join(',') === '5.4,9,14.4', 'az ablak arányos a licittel', win.easy.join(','));
  ok(win.extreme3 === 4, 'extrém szinten alsó korlát véd (2,4 mp helyett 4)', win.extreme3);
  ok(win.bounds.join(',') === '3,5', 'a licit alsó határa 3, alapból 5', win.bounds.join(','));
  // ⚠️ v10.350: NINCS felso hatar — a konstansnak sem szabad leteznie
  ok(win.noMax === 'undefined', 'nincs OTDOLOG_MAX_BID konstans', win.noMax);
  ok(win.big === 36, 'a nagy licit ablaka is arányos (20 szó, könnyű → 36 mp)', win.big);

  // ── 2. A LICIT-VALASZTO ──
  console.log('\n===== 2. A LICIT-VALASZTO =====');
  await mount(p, 'easy');
  await p.waitForTimeout(900);
  const t0 = await txt(p);
  // ⚠️ v10.350: a „<Nev> licitál" sor KIKERULT — a footer pirulaja mondja meg,
  // ki jon, a lap tetejen ugyanaz a nev feleslegesen ismetlodott.
  ok(!/licitál/i.test(t0), 'NINCS „<név> licitál" sor a lapon', t0.slice(0, 90));
  ok(/Hány szót vállalsz/i.test(t0), 'a kérdés viszont ott van');
  ok(/Kecsi/.test(t0) && /iszik/.test(t0), 'kiírja, mi múlik rajta (a páros tétje)', t0.slice(0, 160));
  ok(await bidNow(p) === 5, 'alapból 5', await bidNow(p));
  ok(/9mp · Indítás/.test(t0), 'és az induló gomb a licithez tartozó időt mutatja', (t0.match(/[\d.]+mp · \S+/) || [])[0]);

  // ⚠️ v10.350: A KATEGORIA MAR A LICIT ALATT LATSZIK. Kategoria nelkul nem
  // lehet ertelmesen szamot vallalni. (A v10.339-ben satirozva volt.)
  const catCard = await p.evaluate(() => {
    const hatch = [...document.querySelectorAll('#__p div')]
      .some(d => /repeating-linear-gradient/.test(d.style.background || ''));
    const txt = document.getElementById('__p').innerText || '';
    const m = txt.match(/KATEGÓRIA\s*\n\s*(.+)/);
    return { hatch, name: m ? m[1].trim() : null };
  });
  ok(!catCard.hatch, 'a kategória NINCS satírozva — a licit alatt is látszik');
  ok(!!catCard.name && catCard.name.length > 2, 'és tényleg ki van írva a neve', catCard.name);

  // ── 2b. ⚠️ A LICITNEK NINCS PLAFONJA ──
  console.log('\n===== 2b. NINCS FELSO HATAR =====');
  await bump(p, +1, 3);
  ok(await bidNow(p) === 8, 'felfelé 8', await bidNow(p));
  await bump(p, +1, 7);
  ok(await bidNow(p) === 15, 'és tovább is megy — 15', await bidNow(p));
  const plusOff = await p.evaluate(() =>
    [...document.querySelectorAll('#__p button')].find(x => x.getAttribute('aria-label') === 'Eggyel több').disabled);
  ok(plusOff === false, 'a „+" gomb sosem tiltódik le', plusOff);
  ok(/27mp/.test(await txt(p)), 'az idő követi a nagy licitet is', (await txt(p)).match(/[\d.]+mp/)[0]);
  await bump(p, -1, 20);
  ok(await bidNow(p) === 3, 'lefelé viszont 3-nál megáll', await bidNow(p));

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
  ok(/licitál|LICITÁL/.test(g.desc) && !/3–8/.test(g.desc),
     'a leírás a licitről szól, és már NEM ígér 3–8-as tartományt', g.desc.slice(0, 120));

  // ── 6. AZ ORA a kozos BohTimer savja, es a jelolok RACSBAN allnak ──
  console.log('\n===== 6. AZ ORA ES A JELOLO-RACS =====');
  await mount(p, 'easy');
  await p.waitForTimeout(900);
  await bump(p, +1, 7);                       // licit = 12
  ok(await bidNow(p) === 12, 'a tét: 12 szó', await bidNow(p));
  await start(p);
  await p.waitForTimeout(300);
  const timer = await p.evaluate(() => {
    const t = document.querySelector('#__p [role="timer"]');
    // a REGI gyuru: 160x160-as svg, benne r=72 kor
    const ring = [...document.querySelectorAll('#__p svg circle')].some(c => c.getAttribute('r') === '72');
    return { has: !!t, h: t ? Math.round(t.getBoundingClientRect().height) : null,
             w: t ? Math.round(t.getBoundingClientRect().width) : null, ring };
  });
  ok(timer.has, 'van visszaszámláló');
  // ⚠️ 30 px, vizszintes — a regi gyuru 160 px-et vett el a lap elol
  ok(timer.h === 30, 'a közös BohTimer magassága (30 px)', timer.h + ' px');
  ok(timer.w > 200, 'és vízszintes, széles', timer.w + ' px');
  ok(!timer.ring, 'a 160 px-es gyűrű ELTŰNT', timer.ring);

  const grid = await p.evaluate('(() => { const r = ' + ROW_JS + '; if (!r) return null;'
    + ' const cs = getComputedStyle(r);'
    + ' const cells = [...r.children].map(c => Math.round(c.getBoundingClientRect().width));'
    + ' const rows = new Set([...r.children].map(c => Math.round(c.getBoundingClientRect().top))).size;'
    + ' return { display: cs.display, cols: cs.gridTemplateColumns.split(" ").length,'
    + '          n: r.children.length, minW: Math.min(...cells), rows }; })()');
  ok(grid && grid.n === 12, 'mind a 12 jelölő kint van', grid && grid.n);
  // ⚠️ Egyetlen `flex` sorban 12 jelolo 20 px szeles lenne — ezert RACS.
  ok(grid && grid.display === 'grid' && grid.cols === 6, 'rácsban, hat oszlopban',
     grid && (grid.display + ' / ' + grid.cols + ' oszlop'));
  ok(grid && grid.rows === 2, 'két sorba tördelve', grid && grid.rows);
  ok(grid && grid.minW >= 40, 'és a csempék olvasható szélesek maradnak', grid && grid.minW + ' px');

  // ── 7. ⚠️ A PLAYSCREEN KEZI GOMBJAI KIMARADNAK ──
  // A jatek maga konyvel (az ora lejartakor mar eldolt az eredmeny), tehat a
  // „Vesztettem / Nyertem!" par egy MASODIK, ellentmondo utat nyitott a ponthoz.
  console.log('\n===== 7. NINCS KEZI GOMB =====');
  const manual = async (gameId) => {
    await p.evaluate((gameId) => {
      const old = document.getElementById('__p'); if (old) old.remove();
      const root = document.createElement('div'); root.id = '__p';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
      document.body.appendChild(root);
      const PL2 = [{ id:'a', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                   { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 }];
      function H() {
        const [ps, setPs] = React.useState(PL2);
        return React.createElement(PlayScreen, {
          go: () => {}, players: ps, setPlayers: setPs, selectedGames: [gameId],
          roomCode: null, gameMeta: { modes: ['points'], difficulty: 'easy' },
          setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {} });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    }, gameId);
    await p.waitForTimeout(2000);
    return p.evaluate(() => ({
      manual: [...document.querySelectorAll('#__p button')]
        .map(b => (b.textContent || '').trim())
        .filter(t => /^(Vesztettem|Nyertem!|Nem sikerült|Megvan!)/.test(t)),
      txt: (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '),
    }));
  };
  const otd = await manual('otdolog');
  ok(otd.manual.length === 0, 'az 5 dolognál NINCS kézi eredmény-gomb',
     otd.manual.join(' | ') || 'egy sem');
  ok(/Hány szót vállalsz/.test(otd.txt), 'de a játék tényleg elindult (licit-lap)', otd.txt.slice(0, 60));

  // ⚠️ A MECHANIZMUS: nem id-alapu kizaras-lista, hanem URES `cta`. Ugyanez a
  // jelzes all minden mas onmagat konyvelo Paros jatekon (erem, tapper,
  // kopapir, ritmus, reakcio, szamsor, cardbattle).
  const cta = await p.evaluate(() => {
    return { otdolog: (SCENARIOS.otdolog.cta || []).length,
             paros: (SCENARIO_DEFAULTS['Páros'].cta || []).length };
  });
  ok(cta && cta.otdolog === 0, 'az 5 dolog `cta`-ja üres', cta && cta.otdolog);
  // KONTROLL: a Paros ALAPERTELMEZES tovabbra is ket gombot ir elo — enelkul a
  // fenti allitas akkor is igaz lenne, ha a gombokat globalisan kivettuk volna.
  ok(cta && cta.paros === 2, 'kontroll: a Páros alapértelmezés viszont MARADT kétgombos', cta && cta.paros);

  // ⚠️ KONTROLL 2 — a HAJTO bizonyitasa. A „nincs gomb" akkor is igaz lenne,
  // ha a szelektorom rossz, vagy ha a gombokat globalisan kivettuk volna.
  // Ezert VISSZAADJUK a `cta`-t futasidoben: a gomboknak ekkor MEG KELL
  // jelenniuk. (Ma egyetlen jatek `cta`-ja sem nem-ures a kizartakon kivul,
  // tehat valodi jatekkal nem lehetne kontrollalni.)
  await p.evaluate(() => { window.__ctaBak = SCENARIOS.otdolog.cta; SCENARIOS.otdolog.cta = ['Nem sikerült', 'Megvan!']; });
  const ctrl = await manual('otdolog');
  await p.evaluate(() => { SCENARIOS.otdolog.cta = window.__ctaBak; });
  ok(ctrl.manual.length === 2, 'kontroll: nem-üres `cta`-val a két gomb MEGJELENIK',
     ctrl.manual.join(' | ') || 'egy sem');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
