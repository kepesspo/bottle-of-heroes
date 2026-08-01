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
async function playDuel(p, challenger, opponent, statsById) {
  await p.evaluate(({ ch, op, st }) => {
    window.__inc = []; window.__ginc = []; window.__ev = []; window.__gev = [];
    window.getStats = id => Promise.resolve(JSON.parse(JSON.stringify(st[id] || {})));
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
  }, { ch: challenger, op: opponent, st: statsById });
  await p.waitForTimeout(400);

  await clickText(p, 'Start');
  await waitAndTap(p);
  await clickText(p, 'Tovább');
  await p.waitForTimeout(200);
  await clickText(p, 'Start');
  await waitAndTap(p);
  await p.waitForTimeout(500);
}

// A vegeredmeny-sorok kiolvasasa: nev, ido, rekord, atlag, rekord-jelveny.
// A "·" elvalaszto egy stilizalt pottyocske (nincs szoveges tartalma), ezert
// darabonkent olvassuk ki a mezoket, nem egy nagy mintaval.
const readRows = p => p.evaluate(() => {
  const root = document.getElementById('__rk');
  const byName = {};
  [...root.querySelectorAll('div')].forEach(d => {
    const t = (d.innerText || '').replace(/\s+/g, ' ').trim();
    const head = t.match(/^(?:🥇 )?([^\s]+) (\d+)ms\b/);
    if (!head) return;
    // EGY jatekos sora: pontosan egy "NNNms" (szokoz nelkul) van benne. A
    // kartya mindketto jatekost tartalmazza — azt igy kizarjuk.
    if ((t.match(/\d+ms\b/g) || []).length !== 1) return;
    const row = {
      name: head[1], ms: +head[2],
      record: /ÚJ REKORD/i.test(t),
      best: (t.match(/Rekord (\d+) ms/i) || [])[1] != null ? +t.match(/Rekord (\d+) ms/i)[1] : null,
      avg: (t.match(/Átlag (\d+) ms/i) || [])[1] != null ? +t.match(/Átlag (\d+) ms/i)[1] : null,
      len: t.length,
    };
    // a legbovebb ilyen doboz a TELJES sor (nev + ido + rekord/atlag)
    if (!byName[row.name] || row.len > byName[row.name].len) byName[row.name] = row;
  });
  return Object.keys(byName).map(k => byName[k]);
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
    { pA: { bestReactionTime: 300, reactionSum: 2000, reactionCount: 4 }, pB: {} });

  const t1 = await txt(p);
  ok(/nyert!/.test(t1), 'a végeredmény-képernyőn vagyunk', t1.slice(0, 60));
  ok(/Rekord/.test(t1) && /Átlag/.test(t1), 'kiírja a rekordot és az átlagot');

  const rows = await readRows(p);
  ok(rows.length === 2, 'mindkét játékosnak van sora', JSON.stringify(rows));

  const sere = rows.find(r => r.name === 'Sere') || {};
  const luca = rows.find(r => r.name === 'Luca') || {};

  // Sere: volt 300 ms-os rekordja, 4 meres 2000 ms osszeggel.
  ok(sere.ms > 0 && sere.ms < 300, 'Sere ideje gyorsabb a régi rekordnál (a teszt azonnal koppint)', sere.ms + ' ms');
  ok(sere.best === sere.ms, 'Sere REKORDJA a mostani idő lett', sere.best + ' ms (régi: 300)');
  ok(sere.record === true, 'Sere "Új rekord" jelvényt kap');
  const expAvg = Math.round((2000 + sere.ms) / 5);
  ok(sere.avg === expAvg, 'Sere ÁTLAGA a mostani kört is tartalmazza', sere.avg + ' ms (várt: ' + expAvg + ')');

  // Luca: nincs elozmenye — az elso meres egyben a rekord es az atlag is,
  // de jelvenyt NEM kap, mert nem volt mit megdontenie.
  ok(luca.best === luca.ms && luca.avg === luca.ms, 'Luca (előzmény nélkül): a rekord és az átlag a mostani idő',
     luca.best + ' / ' + luca.avg + ' ms (idő: ' + luca.ms + ')');
  ok(luca.record === false, 'Luca NEM kap "Új rekord" jelvényt (nem volt mit megdöntenie)');
  ok(/Az átlag most kezdett gyűlni/.test(t1), 'megmondja, hogy az átlag most kezdett gyűlni');

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
    { pB: { bestReactionTime: 250, reactionSum: 1000, reactionCount: 2 } });

  const t3 = await txt(p);
  const rows3 = await readRows(p);
  const guest = rows3.find(r => r.name === 'Vendeg') || {};
  const luca3 = rows3.find(r => r.name === 'Luca') || {};
  ok(guest.best === null && guest.avg === null, 'profil nélkül NINCS rekord/átlag sor', JSON.stringify(guest));
  ok(luca3.best !== null, 'a profilos játékosnak viszont van', JSON.stringify(luca3));
  ok(luca3.avg === Math.round((1000 + luca3.ms) / 3), 'az ő átlaga is a mostani körrel együtt',
     luca3.avg + ' ms (' + luca3.ms + ' ms-mal)');
  const inc3 = await p.evaluate(() => window.__inc);
  ok(inc3.length === 1 && inc3[0].pid === 'pB', 'profil nélküli játékosról nem írunk semmit', JSON.stringify(inc3.map(x => x.pid)));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.screenshot({ path: path.join(__dirname, 'reakcio_result.png') });
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
