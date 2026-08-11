// v10.332 — Útvesztő: a csapda-leírás nem szakadhat el a viselkedéstől
//
// A leírás és a viselkedés két helyen élt, és el is csúszott:
//   • „Fal — 3 lépés késés"  → valójában ÖTÖT ad (3 megállás + 2 visszapattanás)
//   • „Örvény — 2 mezővel visszadobja" → a pozíció NEM változik, csak 3 lépést
//     veszít (két visszasodrás + visszatérés)
//   • „Teleport — random pozícióra ugrik" → ez a LEGENYHÉBB: +1 lépés
//
// Innentől a `UTVESZTO_TRAPS[].steps()` MAGA a viselkedés (a `buildAnim` ezt
// fűzi a sorba), a `delay` pedig ugyanennek a hossza. Ez a teszt a kettőt veti
// össze — ha valaki a lépéseket átírja, de a számot nem, itt bukik.
//
// Miért „lépés" a mértékegység? A győztes az, akinek KEVESEBB lépése van
// (`steps: seq.length`), tehát a késleltetés pontosan ennyi lépéssel ront.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // ── 1. a kiirt szam = a valodi lepesszam ──
  console.log('\n===== 1. A LEIRAS = A VISELKEDES =====');
  const data = await p.evaluate(() => UTVESZTO_TRAPS.map(t => ({
    id: t.id, name: t.name, korty: t.korty, delay: t.delay, note: t.note,
    // tipikus helyzet: a palya kozepen, van elozo es azelotti mezo is
    real: t.steps({ idx: 12, prev: 11, prev2: 10, jumpIdx: 3 }).length,
    label: utvesztoEffect(t),
  })));
  ok(data.length === 5, 'öt csapdatípus', data.length);
  data.forEach(t => ok(t.real === t.delay,
    `${t.name}: a kiírt „+${t.delay} lépés" = a tényleges lépésszám`, t.real));

  // ── 2. a konkret szamok (a regi, hibas leirasok itt buknanak) ──
  console.log('\n===== 2. A KONKRET SZAMOK =====');
  const by = id => data.find(t => t.id === id);
  ok(by('sorc').delay === 2 && by('sorc').korty === 2, 'Sörcsokor: +2 korty · +2 lépés',
     by('sorc').label);
  ok(by('fal').delay === 5 && by('fal').korty === 3,
     'Fal: +3 korty · +5 lépés (a régi leírás 3-at ígért)', by('fal').label);
  ok(by('alom').delay === 4 && by('alom').korty === 0, 'Álom: korty nélkül, +4 lépés', by('alom').label);
  ok(by('orv').delay === 3 && by('orv').korty === 0,
     'Örvény: +3 lépés (a pozíció NEM változik — a régi leírás mást állított)', by('orv').label);
  ok(by('tel').delay === 1 && by('tel').korty === 0,
     'Teleport: +1 lépés — ez a LEGENYHÉBB csapda', by('tel').label);
  ok(data.every(t => !t.korty || /korty/.test(t.label)), 'ahol van korty, ott ki is van írva');
  ok(!/korty/.test(by('alom').label), 'ahol nincs korty, ott nem ír korty-számot', by('alom').label);

  // ── 3. a jatek LEIRASA is felsorolja oket ──
  console.log('\n===== 3. A JATEK LEIRASA =====');
  const desc = await p.evaluate(() => (GAMES.find(g => g.id === 'utveszto') || {}).desc || '');
  ok(/lerakható csapdák/i.test(desc), 'a leírás bevezeti a csapda-listát');
  data.forEach(t => ok(desc.includes(t.name) && desc.includes(t.label),
    `a leírásban ott a ${t.name} a pontos hatásával`, t.label));

  // ── 4. a lerako felulet: a hatas MAR valasztas elott latszik ──
  console.log('\n===== 4. A LERAKO FELULET =====');
  await p.evaluate(() => {
    const pl = [{ id:'a', name:'Sere', color:'#E07A5F' }, { id:'b', name:'Kecsi', color:'#4FC2A0' }];
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(UtvesztoGame, {
      gameIdx: 0, challenger: pl[0], opponent: pl[1], players: pl,
      onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, gameMeta: {},
    }));
  });
  await p.waitForTimeout(1300);
  // intro → a csapda-lista mar itt kint van
  const introTxt = await p.evaluate(() => document.getElementById('__p').innerText);
  ok(/CSAPDÁK/.test(introTxt), 'az intróban ott a CSAPDÁK blokk');
  ok(data.every(t => introTxt.includes(t.note)), 'minden csapdához ott a magyarázat is',
     data.filter(t => !introTxt.includes(t.note)).map(t => t.name).join(',') || 'mind');

  // tovabb a lerakashoz
  await p.evaluate(() => {
    const x = [...document.querySelectorAll('#__p button')].filter(y => (y.innerText || '').trim());
    if (x.length) x[x.length - 1].click();
  });
  await p.waitForTimeout(900);
  const btns = await p.evaluate(() => [...document.querySelectorAll('#__p button')]
    .map(x => (x.innerText || '').replace(/\s+/g, ' ').trim())
    .filter(t => /Sörcsokor|Fal|Álom|Örvény|Teleport/.test(t)));
  ok(btns.length === 5, 'öt csapda-gomb a lerakó felületen', btns.length);
  ok(btns.every(t => /\+\d+ lépés/.test(t)),
     'MINDEGYIK gombon ott a hatás — nem csak a kiválasztott alatt', JSON.stringify(btns));
  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));

  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
