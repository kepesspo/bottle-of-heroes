// v10.252 — Reakció Teszt: rekord + átlag a végeredményen
//
// Amit ellenőriz:
//   1. a végeredmény-soron megjelenik a REKORD és az ÁTLAG
//   2. a számok a MOSTANI kört is tartalmazzák (= ez lesz a statisztikában is)
//   3. "Új rekord" jelvény CSAK akkor, ha volt korábbi rekord és most jobb lett
//   4. profil nélküli (alkalmi) játékosnál nincs sor — nincs mit viszonyítani
//   5. az átlaghoz szükséges összeg + darabszám tényleg kiíródik, és naplózódik
//      is (különben az Admin/Partik visszavonás elrontaná a statisztikát)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const stub = fs.readFileSync(path.join(__dirname, 'fbstub.js'), 'utf8');

let fail = 0;
const ok = (cond, name, extra) => {
  console.log((cond ? '  OK  ' : '  HIBA') + '   ' + name + (extra !== undefined ? '  → ' + extra : ''));
  if (!cond) fail++;
};

const txt = p => p.evaluate(() => (document.getElementById('__rk') || document.body).innerText.replace(/\s+/g, ' '));

const clickText = (p, re) => p.evaluate(rx => {
  const root = document.getElementById('__rk');
  const b = [...root.querySelectorAll('button')].find(x => new RegExp(rx).test(x.innerText || ''));
  if (b) { b.click(); return true; }
  return false;
}, re);

// Megvarjuk a zold "MOST!" mezot, majd rakoppintunk. A varakozas 1500 ms
// (a Math.random stub miatt), de nem erre epitunk — figyeljuk a szoveget.
async function waitAndTap(p) {
  for (let i = 0; i < 60; i++) {
    const t = await txt(p);
    if (/MOST!/.test(t)) break;
    await p.waitForTimeout(100);
  }
  await p.evaluate(() => {
    const root = document.getElementById('__rk');
    const el = [...root.querySelectorAll('div')].find(x => /Koppints!/.test(x.innerText || ''));
    (el || root.firstElementChild).click();
  });
  await p.waitForTimeout(250);
}

// Egy teljes parbaj lejatszasa a UI-n keresztul, a megadott jatekosokkal.
async function playDuel(p, challenger, opponent, statsById, gameStats) {
  await p.evaluate(({ ch, op, st, gs }) => {
    window.__inc = []; window.__ginc = []; window.__ev = []; window.__gev = [];
    window.getStats = id => Promise.resolve(JSON.parse(JSON.stringify(st[id] || {})));
    // gs === false: a jatek-statisztika egyaltalan nem elerheto
    if (gs === false) delete window.getGameStats;
    else window.getGameStats = () => Promise.resolve(JSON.parse(JSON.stringify(gs || {})));
    window.incrementStats = (pid, inc, best) => { window.__inc.push({ pid, inc, best }); return Promise.resolve(); };
    window.incrementGameStats = (gid, inc, best) => { window.__ginc.push({ gid, inc, best }); return Promise.resolve(); };
    window.logStatEvent = (pid, d) => { window.__ev.push({ pid, d }); return Promise.resolve(); };
    window.logGameStatEvent = (gid, d) => { window.__gev.push({ gid, d }); return Promise.resolve(); };
    Math.random = () => 0;   // a varakozas mindig 1500 ms

    const old = document.getElementById('__rk');
    if (old) old.remove();
    const root = document.createElement('div');
    root.id = '__rk';
    root.style.cssText = 'position:fixed;inset:0;background:#EAF2FB;padding:16px;overflow:auto;z-index:9';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(ReakcioGame, {
      challenger: ch, opponent: op, onAdvance: () => {}, onResult: () => {},
    }));
  }, { ch: challenger, op: opponent, st: statsById, gs: gameStats === false ? false : (gameStats || null) });
  await p.waitForTimeout(400);

  await clickText(p, 'Start');
  await waitAndTap(p);
  await clickText(p, 'Tovább');
  await p.waitForTimeout(200);
  await clickText(p, 'Start');
  await waitAndTap(p);
  await p.waitForTimeout(500);
}

// Ket kartyat olvasunk ki:
//   - a FELSO (sav-diagram): nev + a mostani ido
//   - az ALSO (viszonyitas): nev | rekord | atlag, harom hasabos racsban
// Az alsot a racs GYEREKEIN vegigmenve olvassuk (fejlec + 3-asaval a sorok),
// mert a szoveg-alapu darabolas itt tobbertelmu lenne.
const readRows = p => p.evaluate(() => {
  const root = document.getElementById('__rk');
  const byName = {};
  [...root.querySelectorAll('div')].forEach(d => {
    const t = (d.innerText || '').replace(/\s+/g, ' ').trim();
    const head = t.match(/^(?:🥇 )?([^\s]+) (\d+)ms\b/);
    if (!head) return;
    // EGY jatekos sora: pontosan egy "NNNms" (szokoz nelkul) van benne.
    if ((t.match(/\d+ms\b/g) || []).length !== 1) return;
    const row = { name: head[1], ms: +head[2], len: t.length };
    if (!byName[row.name] || row.len < byName[row.name].len) byName[row.name] = row;
  });
  return Object.keys(byName).map(k => byName[k]);
});

const readHistCard = p => p.evaluate(() => {
  const root = document.getElementById('__rk');
  // a racs: gridTemplateColumns harom hasabbal, a fejlecben REKORD + ATLAG
  const grid = [...root.querySelectorAll('div')].find(d =>
    getComputedStyle(d).display === 'grid' &&
    /REKORD/i.test(d.innerText || '') && /ÁTLAG/i.test(d.innerText || ''));
  if (!grid) return null;
  const cells = [...grid.children];
  // A fejlec utan 3-asaval jonnek a sorok. Az ures cellak (a fejlec ures
  // helykitoltoje, es a mindenkori sort elvalaszto vonal) kimaradnak.
  const body = cells.slice(3).filter(c => (c.innerText || '').trim() !== '');
  const rows = [];
  for (let i = 0; i + 2 < body.length; i += 3) {
    const bestTxt = (body[i + 1].innerText || '').replace(/\s+/g, ' ');
    const avgTxt = (body[i + 2].innerText || '').replace(/\s+/g, ' ');
    rows.push({
      name: (body[i].innerText || '').trim(),
      best: +(bestTxt.match(/(\d+) ms/) || [])[1] || null,
      avg: +(avgTxt.match(/(\d+) ms/) || [])[1] || null,
      record: /ÚJ REKORD/i.test(bestTxt),
      bestGreen: getComputedStyle(body[i + 1].querySelector('span') || body[i + 1]).color,
    });
  }
  return {
    rows,
    labels: [...cells.slice(0, 3)].map(c => (c.innerText || '').trim()),
    fresh: /Az átlag most kezdett gyűlni/.test(grid.parentElement.innerText || ''),
    // a kartya ugyanaz a doboz-stilus, mint a felette levo eredmeny-kartya
    css: (() => { const s = getComputedStyle(grid.parentElement); return { r: s.borderRadius, bg: s.backgroundColor, w: Math.round(grid.parentElement.getBoundingClientRect().width) }; })(),
  };
});

// A felso (sav-diagramos) kartya stilusa. A kulso csomagolo is tartalmazza
// mindket idot, ezert a HATTERRE is szurunk — a kartya az, ami fest.
const cardCss = p => p.evaluate(() => {
  const root = document.getElementById('__rk');
  const card = [...root.querySelectorAll('div')].find(d =>
    ((d.innerText || '').match(/\d+ms\b/g) || []).length === 2 &&
    getComputedStyle(d).backgroundColor !== 'rgba(0, 0, 0, 0)');
  if (!card) return null;
  const s = getComputedStyle(card);
  return { r: s.borderRadius, bg: s.backgroundColor, w: Math.round(card.getBoundingClientRect().width) };
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  console.log('\n===== 1. VAN ELŐZMÉNY vs. NINCS ELŐZMÉNY =====');
  await playDuel(p,
    { id: 'a', name: 'Sere', profileId: 'pA' },
    { id: 'b', name: 'Luca', profileId: 'pB' },
    { pA: { bestReactionTime: 300, reactionSum: 2000, reactionCount: 4 }, pB: {} },
    // a mindenkori csucs 20 ms — ezt a teszt (kb. 50 ms) nem donti meg
    { bestReactionTime: 20, reactionSum: 5000, reactionCount: 10 });

  const t1 = await txt(p);
  ok(/nyert!/.test(t1), 'a végeredmény-képernyőn vagyunk', t1.slice(0, 60));
  // a feliratok CSS-bol nagybetusek — az innerText is nagybetut ad vissza
  ok(/REKORD/i.test(t1) && /ÁTLAG/i.test(t1), 'kiírja a rekordot és az átlagot');

  const rows = await readRows(p);
  ok(rows.length === 2, 'a felső kártyán mindkét játékos ideje ott van', JSON.stringify(rows));

  const card = await readHistCard(p);
  ok(card !== null, 'van külön kártya a rekordnak és az átlagnak');
  ok(/🏅/.test(card.labels[1]) && /REKORD/i.test(card.labels[1]), 'a rekord hasáb fel van címkézve', card.labels[1]);
  ok(/📊/.test(card.labels[2]) && /ÁTLAG/i.test(card.labels[2]), 'az átlag hasábon emoji + felirat', card.labels[2]);

  const top = await cardCss(p);
  ok(card.css.r === top.r && card.css.bg === top.bg && card.css.w === top.w,
     'ugyanolyan doboz, mint a fölötte lévő eredmény-kártya',
     JSON.stringify(card.css) + ' vs ' + JSON.stringify(top));

  const sere = rows.find(r => r.name === 'Sere') || {};
  const luca = rows.find(r => r.name === 'Luca') || {};
  const hSere = card.rows.find(r => r.name === 'Sere') || {};
  const hLuca = card.rows.find(r => r.name === 'Luca') || {};
  const isG = r => /Mindenki/.test(r.name);
  const gRow = card.rows.find(isG);
  ok(card.rows.filter(r => !isG(r)).length === 2, 'a kártyán mindkét játékosnak van sora',
     JSON.stringify(card.rows.filter(r => !isG(r))));

  // Sere: volt 300 ms-os rekordja, 4 meres 2000 ms osszeggel.
  ok(sere.ms > 0 && sere.ms < 300, 'Sere ideje gyorsabb a régi rekordnál (a teszt azonnal koppint)', sere.ms + ' ms');
  ok(hSere.best === sere.ms, 'Sere REKORDJA a mostani idő lett', hSere.best + ' ms (régi: 300)');
  ok(hSere.record === true, 'Sere "Új rekord" jelvényt kap');
  const expAvg = Math.round((2000 + sere.ms) / 5);
  ok(hSere.avg === expAvg, 'Sere ÁTLAGA a mostani kört is tartalmazza', hSere.avg + ' ms (várt: ' + expAvg + ')');

  // Luca: nincs elozmenye — az elso meres egyben a rekord es az atlag is,
  // de jelvenyt NEM kap, mert nem volt mit megdontenie.
  ok(hLuca.best === luca.ms && hLuca.avg === luca.ms, 'Luca (előzmény nélkül): a rekord és az átlag a mostani idő',
     hLuca.best + ' / ' + hLuca.avg + ' ms (idő: ' + luca.ms + ')');
  ok(hLuca.record === false, 'Luca NEM kap "Új rekord" jelvényt (nem volt mit megdöntenie)');
  ok(card.fresh, 'megmondja, hogy az átlag most kezdett gyűlni');

  // Mindenkori sor: a csucs 20 ms volt, azt a teszt (~50 ms) nem donti meg.
  // Az atlagba MINDKET mostani ido beleszamit: (5000 + t1 + t2) / 12.
  ok(gRow !== undefined, 'van "Mindenki" sor a mindenkori értékekkel', gRow && JSON.stringify(gRow));
  ok(/🌍/.test(gRow.name), 'a sor emojival van jelölve', gRow.name);
  ok(gRow.best === 20, 'a mindenkori csúcs marad, ha ez a kör nem döntötte meg', gRow.best + ' ms');
  const expG = Math.round((5000 + sere.ms + luca.ms) / 12);
  ok(gRow.avg === expG, 'a mindenkori átlagba MINDKÉT mostani idő beleszámít',
     gRow.avg + ' ms (várt: ' + expG + ')');
  ok(card.rows[card.rows.length - 1] === gRow || isG(card.rows[card.rows.length - 1]),
     'a mindenkori sor a játékosok ALATT van');

  await p.screenshot({ path: path.join(__dirname, 'reakcio_result.png') });

  console.log('\n===== 2. AMIT A STATISZTIKÁBA ÍRUNK =====');
  const inc = await p.evaluate(() => window.__inc);
  const ginc = await p.evaluate(() => window.__ginc);
  const ev = await p.evaluate(() => window.__ev);
  const gev = await p.evaluate(() => window.__gev);

  ok(inc.length === 2, 'mindkét profilnak írunk', JSON.stringify(inc));
  const iA = inc.find(x => x.pid === 'pA') || {};
  ok(iA.inc && iA.inc.reactionCount === 1 && iA.inc.reactionSum === sere.ms,
     'összeg + darabszám megy ki (ebből lesz az átlag)', JSON.stringify(iA.inc));
  ok(iA.best && iA.best.bestReactionTime === sere.ms, 'a rekord-jelölt is megy (a szerver dönt róla)', JSON.stringify(iA.best));

  ok(ev.length === 2, 'naplózzuk is — az Admin/Partik visszavonás így pontos', JSON.stringify(ev.map(x => x.pid)));
  ok(ev.every(x => x.d.reactionCount === 1), 'a napló ugyanazt a deltát tartalmazza');

  ok(ginc.length === 1 && ginc[0].gid === 'reakcio', 'a játék-statisztika is frissül');
  ok(ginc[0].inc.reactionCount === 2, 'a játék átlagába MINDKÉT idő beleszámít', JSON.stringify(ginc[0].inc));
  ok(ginc[0].inc.reactionSum === sere.ms + luca.ms, 'a játék-összeg a két idő összege',
     ginc[0].inc.reactionSum + ' = ' + sere.ms + ' + ' + luca.ms);
  ok(ginc[0].best.bestReactionTime === Math.min(sere.ms, luca.ms), 'a játék rekordja a gyorsabb idő');
  ok(gev.length === 1 && gev[0].gid === 'reakcio', 'a játék-esemény is naplózódik');

  console.log('\n===== 3. PROFIL NÉLKÜLI (ALKALMI) JÁTÉKOS =====');
  await playDuel(p,
    { id: 'a', name: 'Vendeg', profileId: null },
    { id: 'b', name: 'Luca', profileId: 'pB' },
    { pB: { bestReactionTime: 250, reactionSum: 1000, reactionCount: 2 } },
    { bestReactionTime: 20, reactionSum: 5000, reactionCount: 10 });

  const rows3 = await readRows(p);
  const card3 = await readHistCard(p);
  const luca3 = rows3.find(r => r.name === 'Luca') || {};
  const pRows3 = card3.rows.filter(r => !/Mindenki/.test(r.name));
  ok(rows3.length === 2, 'a felső kártyán továbbra is mindkét idő ott van', JSON.stringify(rows3));
  ok(pRows3.length === 1 && pRows3[0].name === 'Luca',
     'a viszonyítás-kártyán CSAK a profilos játékos szerepel', JSON.stringify(pRows3));
  ok(pRows3[0].avg === Math.round((1000 + luca3.ms) / 3), 'az ő átlaga is a mostani körrel együtt',
     pRows3[0].avg + ' ms (' + luca3.ms + ' ms-mal)');
  // A mindenkori sor a profil nelkuli jatekos idejet IS szamolja — az is
  // beleszamit a jatek statisztikajaba.
  const g3 = card3.rows.find(r => /Mindenki/.test(r.name)) || {};
  const guest3 = rows3.find(r => r.name === 'Vendeg') || {};
  ok(g3.avg === Math.round((5000 + guest3.ms + luca3.ms) / 12),
     'a mindenkori átlagba a profil nélküli játékos ideje is beleszámít', g3.avg + ' ms');
  const inc3 = await p.evaluate(() => window.__inc);
  ok(inc3.length === 1 && inc3[0].pid === 'pB', 'profil nélküli játékosról nem írunk semmit', JSON.stringify(inc3.map(x => x.pid)));

  console.log('\n===== 4. EGYIK JÁTÉKOSNAK SINCS PROFILJA =====');
  // A mindenkori sor ilyenkor is ervenyes — az nem egy jatekosrol szol.
  await playDuel(p,
    { id: 'a', name: 'Vendeg', profileId: null },
    { id: 'b', name: 'Masik', profileId: null }, {},
    { bestReactionTime: 20, reactionSum: 5000, reactionCount: 10 });
  const card4 = await readHistCard(p);
  ok(card4 !== null && card4.rows.length === 1 && /Mindenki/.test(card4.rows[0].name),
     'a kártyán CSAK a mindenkori sor marad', card4 && JSON.stringify(card4.rows));
  ok(card4.rows[0].best === 20, 'a mindenkori csúcs ilyenkor is látszik', card4.rows[0].best + ' ms');

  console.log('\n===== 5. MEGDŐL A MINDENKORI CSÚCS =====');
  await playDuel(p,
    { id: 'a', name: 'Sere', profileId: 'pA' },
    { id: 'b', name: 'Luca', profileId: 'pB' },
    { pA: {}, pB: {} },
    { bestReactionTime: 900, reactionSum: 9000, reactionCount: 10 });
  const card5 = await readHistCard(p);
  const rows5 = await readRows(p);
  const g5 = card5.rows.find(r => /Mindenki/.test(r.name)) || {};
  const fastest5 = Math.min(...rows5.map(r => r.ms));
  ok(g5.best === fastest5, 'a mindenkori csúcs a mostani gyorsabb időre javul',
     g5.best + ' ms (régi: 900)');
  ok(/rgb\(/.test(g5.bestGreen) && g5.bestGreen !== 'rgb(0, 0, 0)', 'a csúcs kiemelve jelenik meg', g5.bestGreen);

  console.log('\n===== 6. NINCS JÁTÉK-STATISZTIKA =====');
  await playDuel(p,
    { id: 'a', name: 'Sere', profileId: 'pA' },
    { id: 'b', name: 'Luca', profileId: 'pB' },
    { pA: { bestReactionTime: 300, reactionSum: 2000, reactionCount: 4 }, pB: {} },
    false);
  const card6 = await readHistCard(p);
  const t6 = await txt(p);
  ok(card6 !== null && !card6.rows.some(r => /Mindenki/.test(r.name)),
     'ha nincs játék-statisztika, a mindenkori sor kimarad — a többi marad', JSON.stringify(card6.rows));
  ok(/nyert!/.test(t6), 'és a végeredmény ugyanúgy látszik', t6.slice(0, 40));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
