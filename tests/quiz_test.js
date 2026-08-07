// v10.237 — a Kvíz nyertese tényleg megkapja a pontot
//
// A végképernyő eddig is kiírta, hogy "+1 pont", de a pont nem került rá a
// játékosra: a QuizGame csak korty-térképet adott az onAdvance-nek, a
// pont-térképet (2. paraméter) soha. Ez a teszt a PLAYERS tömböt nézi, nem a
// feliratot — pont azért, mert a felirat korábban is jó volt.
//
// Amit ellenőriz:
//   1. helyes válasz → "Bankolom" → kiosztás "Mentés ✓" → +1 pont a kihívónak,
//      és a kiosztott korty a másik játékosra kerül
//   2. helyes válasz → "Bankolom" → "Kihagyom" → +1 pont, korty senkinek
//   3. rossz válasz → nincs pont, a kihívó iszik
//
// Determinizmus: a Kvíz a kérdéseket ÉS a válaszokat is
// `sort(() => Math.random() - 0.5)`-tel keveri. Math.random()=0.5 mellett a
// komparátor pontosan 0-t ad, a sort pedig stabil (ES2019 óta a spec is így
// írja elő), tehát a sorrend változatlan marad — így az "A" válasz mindig a
// helyes (a forrásban a[0] a jó megoldás). 0-val NEM működne: az állandóan
// negatív komparátor a V8-ban megfordítja a tömböt.
//
// A pont csak a Kövi gomb megnyomásakor kerül be (pendingCommit minta), ezért
// a mérés előtt mindig meg kell nyomni a Kövi-t.
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

const clickText = (p, re) => p.evaluate(r => {
  const rx = new RegExp(r);
  const b = [...document.querySelectorAll('button')].find(x => rx.test((x.innerText || '').replace(/\s+/g, ' ')));
  if (b) b.click();
  return !!b;
}, re.source);

const clickLetter = (p, letter) => p.evaluate(l => {
  const b = [...document.querySelectorAll('button')].find(x => new RegExp('^' + l + '\\n').test(x.innerText || ''));
  if (b) b.click();
  return b ? (b.innerText || '').replace('\n', ' ') : null;
}, letter);

const players = p => p.evaluate(() => (window.__players || []).map(x => ({ n: x.name, pts: x.points, dr: x.drinks })));

async function fresh(b) {
  const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}
    Math.random = function(){ return 0.5; };`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column';
    document.body.appendChild(root);
    function H() {
      const [pl, setPl] = React.useState([
        { id: 'a', name: 'Sere', color: '#E07A5F', points: 0, drinks: 0 },
        { id: 'b', name: 'Kecsi', color: '#4FC2A0', points: 0, drinks: 0 },
        { id: 'c', name: 'Vivi', color: '#A78BFA', points: 0, drinks: 0 },
      ]);
      window.__players = pl;
      return React.createElement(PlayScreen, {
        go: () => {}, players: pl, setPlayers: setPl, selectedGames: ['quiz'],
        roomCode: null, gameMeta: { modes: ['points'], difficulty: 'mid' }, setGameMeta: () => {},
        setScoreHistory: () => {}, setLastGameRound: () => {},
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(2400);
  return p;
}

// A pont csak a Kovi gombra kerul be (pendingCommit)
const commit = async (p) => {
  await p.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find(x => /Kövi/.test(x.innerText || ''));
    if (b) b.click();
  });
  await p.waitForTimeout(1500);
};

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. bankolás + korty kiosztása ──
  console.log('\n===== BANKOLÁS + KIOSZTÁS =====');
  let p = await fresh(b);
  const picked = await clickLetter(p, 'A');
  await p.waitForTimeout(800);
  ok(await p.evaluate(() => [...document.querySelectorAll('button')].some(x => /Bankolom/.test(x.innerText || ''))),
     'helyes válasz → megjelenik a Bankolom gomb', picked);
  await clickText(p, /Bankolom/);
  await p.waitForTimeout(900);
  ok(await p.evaluate(() => /kiosztja — kire\?/.test(document.body.innerText)), 'megnyílik a korty-kiosztó');
  // v10.315: a kioszto a KOZOS PlayerDrinkRow-t hasznalja, mint a Buntetes es a
  // tobbi felulet. A leptetok SVG-k, nincs szoveges „+" — az aria-label a fogodzo
  // (ugyanaz, amire a ledger_test / sohanem_test / penalty_unified_test kattint).
  await p.evaluate(() => {
    const plus = [...document.querySelectorAll('button[aria-label="Egy korttyal több"]')];
    if (plus[0]) plus[0].click();
  });
  await p.waitForTimeout(400);
  await clickText(p, /Mentés/);
  await p.waitForTimeout(1200);
  await commit(p);
  let st = await players(p);
  let scorer = st.filter(x => x.pts > 0), drinker = st.filter(x => x.dr > 0);
  ok(scorer.length === 1 && scorer[0].pts === 1, 'a bankoló pontosan 1 pontot kapott', JSON.stringify(st));
  ok(drinker.length === 1, 'a kiosztott korty egy másik játékosra került', JSON.stringify(st));
  ok(scorer.length && drinker.length && scorer[0].n !== drinker[0].n,
     'nem ugyanaz pontozott és ivott', (scorer[0] || {}).n + ' / ' + (drinker[0] || {}).n);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 2. bankolás, de a kiosztás kihagyva ──
  console.log('\n===== BANKOLÁS + KIHAGYOM =====');
  p = await fresh(b);
  await clickLetter(p, 'A');
  await p.waitForTimeout(800);
  await clickText(p, /Bankolom/);
  await p.waitForTimeout(900);
  await clickText(p, /Kihagyom/);
  await p.waitForTimeout(1200);
  await commit(p);
  st = await players(p);
  scorer = st.filter(x => x.pts > 0);
  ok(scorer.length === 1 && scorer[0].pts === 1, 'kiosztás nélkül is jár az 1 pont', JSON.stringify(st));
  ok(st.every(x => x.dr === 0), 'senki nem ivott', JSON.stringify(st));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 3. rossz válasz ──
  console.log('\n===== ROSSZ VÁLASZ =====');
  p = await fresh(b);
  const wrong = await clickLetter(p, 'B');
  await p.waitForTimeout(2400);
  // Rossz valasznal a jatek NEM lep 'done' fazisba (1,5 mp utan egybol jon a
  // result banner), ezert a "Rossz válasz" felirat sose latszik. A biztos jel:
  // nincs Bankolom gomb — tehat nem helyes valasz ment be.
  ok(!(await p.evaluate(() => [...document.querySelectorAll('button')].some(x => /Bankolom/.test(x.innerText || '')))),
     'rossz válasz ment be (nincs Bankolom gomb)', wrong);
  await commit(p);
  st = await players(p);
  ok(st.every(x => x.pts === 0), 'rossz válaszért NINCS pont', JSON.stringify(st));
  ok(st.filter(x => x.dr > 0).length === 1, 'a kihívó iszik', JSON.stringify(st));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
