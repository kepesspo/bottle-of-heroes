// v10.173 — Ország-Város: "Várjuk meg a kör végét"
//
// Eddig ha valaki keszen lett, a tobbieknek 10 mp maradt — akkor is, ha a
// korido meg boven tartott volna. Az uj kapcsoloval a teljes korido lejar.
//
// A hataridot a hoszt es a vendeg oldala korabban KULON masolatban szamolta.
// Most egy fuggveny (ovfjRemaining), es azt kozvetlenul merjuk — igy a
// hataresetek (ido nelkuli kor, meg nem kesz senki) is ellenorizhetok.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 390, height: 1000 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`
    try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
    ['profiles','stats','game_stats','statEvents','gameStatEvents','seasons','usage','config']
      .forEach(k => window.__fbStore[k] = {});
  `);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);

  // ─── 1) A hatarido-szamitas ───
  console.log('\n===== A HATÁRIDŐ-SZÁMÍTÁS =====');
  const calc = await p.evaluate(() => {
    const now = Date.now();
    const R = (o) => ovfjRemaining(Object.assign({ phase: 'writing', writingStart: now }, o));
    return {
      // 90 mp-es kor, valaki epp most lett kesz
      grace:    R({ roundTime: 90, doneAt: now, waitFullTime: false }),
      full:     R({ roundTime: 90, doneAt: now, waitFullTime: true }),
      // meg senki nem kesz — mindket esetben a teljes korido
      nobodyA:  R({ roundTime: 90, doneAt: null, waitFullTime: false }),
      nobodyB:  R({ roundTime: 90, doneAt: null, waitFullTime: true }),
      // ido nelkuli kor: a 10 mp az EGYETLEN lezaro — a kapcsolo nem szamit
      noTimeA:  R({ roundTime: null, doneAt: now, waitFullTime: false }),
      noTimeB:  R({ roundTime: null, doneAt: now, waitFullTime: true }),
      noTimeNobody: R({ roundTime: null, doneAt: null, waitFullTime: true }),
      // nem az irasi fazisban vagyunk
      notWriting: ovfjRemaining({ phase: 'voting', roundTime: 90, writingStart: now, doneAt: now }),
      // rovid korido: a 10 mp nem nyujthatja meg
      shorter:  ovfjRemaining({ phase:'writing', roundTime: 5, writingStart: now, doneAt: now, waitFullTime: false }),
    };
  });
  ok('alapból 10 mp marad, ha valaki kész', calc.grace === 10, calc.grace);
  ok('bekapcsolva a teljes köridő lejár', calc.full === 90, calc.full);
  ok('ha még senki nem kész, mindkét esetben a teljes köridő',
     calc.nobodyA === 90 && calc.nobodyB === 90, `${calc.nobodyA} / ${calc.nobodyB}`);
  // Ido nelkuli kornel a 10 mp az egyetlen, ami lezarja — ha a kapcsolo itt is
  // hatna, a kor SOSEM erne veget. Ezert szandekosan figyelmen kivul marad.
  ok('idő nélküli körnél a kapcsoló nem számít', calc.noTimeA === 10 && calc.noTimeB === 10,
     `${calc.noTimeA} / ${calc.noTimeB}`);
  ok('idő nélkül és senki nem kész → nincs visszaszámlálás', calc.noTimeNobody === null, calc.noTimeNobody);
  ok('íráson kívül nincs visszaszámlálás', calc.notWriting === null, calc.notWriting);
  ok('a 10 mp nem hosszabbítja meg a rövidebb kört', calc.shorter === 5, calc.shorter);

  // ─── 2) A beallito lap ───
  console.log('\n===== A BEÁLLÍTÓ LAP =====');
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__c';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg)';
    document.body.appendChild(root);
    function H() { const [c, sc] = React.useState({}); window.__cfg = c;
      return React.createElement(OVFJConfigSheet, { config: c, setConfig: sc, onClose: () => {} }); }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(1400);
  const txt = () => p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  // A lap portalban renderel — nem a mount-konteneren belul kell keresni.
  const flip = () => p.evaluate(() => {
    const lbl = [...document.querySelectorAll('div')].find(d => d.textContent.trim() === 'Várjuk meg a kör végét');
    if (!lbl) return false;
    const mid = e => { const r = e.getBoundingClientRect(); return r.top + r.height / 2; };
    const sw = [...document.querySelectorAll('div')].filter(x => {
      const r = x.getBoundingClientRect(); return Math.round(r.width) === 52 && Math.round(r.height) === 32; });
    if (!sw.length) return false;
    sw.sort((a, c) => Math.abs(mid(a) - mid(lbl)) - Math.abs(mid(c) - mid(lbl)));
    sw[0].click(); return true;
  });

  ok('a kapcsoló megjelenik', /Várjuk meg a kör végét/.test(await txt()));
  ok('alapból a 10 mp-es viselkedést írja', /Ha valaki kész, a többieknek 10 mp marad/.test(await txt()));
  ok('a kapcsoló megtalálható', await flip() === true);
  await p.waitForTimeout(500);
  ok('bekapcsolva a configba kerül',
     (await p.evaluate(() => window.__cfg)).waitFullTime === true,
     JSON.stringify(await p.evaluate(() => window.__cfg)));
  ok('a magyarázat is átvált', /mindig végig lejár/.test(await txt()));

  // "Idő nélkül" korido: a kapcsolo nem valaszthato
  await p.evaluate(() => {
    const btn = [...document.querySelectorAll('button')].find(x => /Idő nélkül/.test(x.innerText));
    if (btn) btn.click();
  });
  await p.waitForTimeout(500);
  ok('idő nélküli körnél megmondja, miért nem választható',
     /nem választható/.test(await txt()), (await txt()).match(/Idő nélküli.{0,60}/) || '—');
  const before = await p.evaluate(() => window.__cfg.waitFullTime);
  await flip(); await p.waitForTimeout(400);
  ok('idő nélküli körnél a kapcsoló nem vált',
     (await p.evaluate(() => window.__cfg.waitFullTime)) === before, `${before} → ${await p.evaluate(() => window.__cfg.waitFullTime)}`);

  // ─── 3) EGY forras ───
  console.log('\n===== EGY FORRÁS =====');
  const src = fs.readFileSync('/home/user/bottle-of-heroes/app.src.html', 'utf8');
  ok('nincs több kézzel írt 10000 ms-os határidő-számítás',
     (src.match(/doneAt \+ 10000/g) || []).length === 0,
     (src.match(/.{0,30}doneAt \+ 10000.{0,20}/) || ['—'])[0]);
  ok('a host és a vendég is ugyanazt a függvényt hívja',
     (src.match(/ovfjRemaining\(/g) || []).length >= 3,
     (src.match(/ovfjRemaining\(/g) || []).length + ' hivatkozás (1 definíció + 2 hívás)');
  ok('a beállítás átmegy a vendégnek is (syncRoom)', /ovfjState: \{[^}]*waitFullTime/.test(src));

  ok('nincs JS hiba', errs.filter(e => !/ServiceWorker/.test(e)).length === 0, errs.join(' | '));
  await p.close();
  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
