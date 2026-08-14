// v10.370 — Hajime / Kéz csere: a korty = a HIBASZAM (abszolút, nehézség nélkül)
//
// A BEJELENTETT HIBA (audit): nehéz szinten a banner „3 KORTY"-ot írt, miközben
// a vesztes a hibaszáma × nehézség-et itta (Sere 3 hiba → 9 korty). Ez a
// pont-büntetés banner-hibájának testvére volt.
//
// A JAVÍTÁS (tulajdonosi döntés, B): a korty MAGA a hibaszám — se nehézség, se
// wildcard nem szorozza (`absolute:true` a bannerben és az advance-ben). A banner
// a TÉNYLEGES számot mutatja: egyenlőnél egy „N KORTY", fejenként másnál a
// névenkénti bontás.
//
// A fogódzó: NEHÉZ szinten Sere 3 hiba / Kecsi 2 hiba → drinks Sere:3, Kecsi:2
// (NEM 9/6), és a banner sem hazudik nagy flat számot.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

async function open(b) {
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3000);
  return p;
}
const mount = (p, game, diff) => p.evaluate(({ game, diff }) => {
  const r = document.getElementById('root'); if (r) r.style.display = 'none';
  const old = document.getElementById('__p'); if (old) old.remove();
  const root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:#EAF2FB';
  document.body.appendChild(root);
  function H() {
    const [ps, setPs] = React.useState([
      { id: 'a', name: 'Sere', color: '#E07A5F', points: 0, drinks: 0 },
      { id: 'b', name: 'Kecsi', color: '#4FC2A0', points: 0, drinks: 0 },
      { id: 'c', name: 'Vivi', color: '#A78BFA', points: 0, drinks: 0 }]);
    window.__players = ps;
    return React.createElement(PlayScreen, { go: () => {}, players: ps, setPlayers: setPs, selectedGames: [game],
      roomCode: null, setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
      gameMeta: { modes: ['points', 'drinks'], difficulty: diff } });
  }
  ReactDOM.createRoot(root).render(React.createElement(H));
}, { game, diff });

const addMistakes = (p, map) => p.evaluate((map) => {
  for (const [name, n] of Object.entries(map)) {
    const rows = [...document.querySelectorAll('#__p div')].filter(d =>
      (d.textContent || '').includes(name) && [...d.querySelectorAll('button')].some(x => x.textContent.trim() === '+'));
    rows.sort((a, b) => a.textContent.length - b.textContent.length);
    const plus = [...rows[0].querySelectorAll('button')].find(x => x.textContent.trim() === '+');
    for (let i = 0; i < n; i++) plus.click();
  }
}, map);
const bannerTxt = p => p.evaluate(() => { const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250'); return el ? (el.innerText || '').replace(/\s+/g, ' ').trim() : ''; });
const stateOf = p => p.evaluate(() => (window.__players || []).map(x => ({ n: x.name, d: x.drinks, pt: x.points })));

async function play(p, game, diff, map) {
  await mount(p, game, diff);
  await p.waitForTimeout(2200);
  await addMistakes(p, map);
  await p.waitForTimeout(300);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__p button')].find(x => /Befejezés/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(1400);
  const banner = await bannerTxt(p);
  await p.evaluate(() => { const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250'); if (el) el.click(); });
  await p.waitForTimeout(400);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__p button')].find(x => /Kövi/i.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(1800);
  return { banner, state: await stateOf(p) };
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  for (const game of ['kezcsere', 'hajime']) {
    // 1. NEHÉZ, fejenként MÁS: Sere 3, Kecsi 2 → drinks 3/2 (NEM 9/6)
    console.log(`\n===== ${game.toUpperCase()} — NEHÉZ, fejenként más (abszolút) =====`);
    {
      const p = await open(b);
      const { banner, state } = await play(p, game, 'hard', { Sere: 3, Kecsi: 2 });
      const sere = state.find(x => x.n === 'Sere'), kecsi = state.find(x => x.n === 'Kecsi'), vivi = state.find(x => x.n === 'Vivi');
      ok(sere.d === 3, `⚠️ Sere 3 hibája = 3 korty (NEM 9 — nincs ×nehézség)`, sere.d);
      ok(kecsi.d === 2, `Kecsi 2 hibája = 2 korty`, kecsi.d);
      ok(vivi.pt === 1, `a hibátlan Vivi +1 pontot kap`, vivi.pt);
      ok(/Sere 3/.test(banner) && /Kecsi 2/.test(banner), 'a banner névenként a valós kortyot írja', (banner.match(/Sere \d[^,]*/) || ['nincs'])[0]);
      ok(!/\b9\b/.test(banner), '⚠️ NINCS a bannerben a régi hazug (skálázott) szám', banner.slice(0, 60));
      ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
      await p.close();
    }
    // 2. NEHÉZ, egyenlő: Sere 3, Kecsi 3 (6 hiba → befejezhető) → drinks 3/3,
    // és mivel egyenlő, a banner „3 KORTY" metrikát mutat (nem 9).
    console.log(`\n===== ${game.toUpperCase()} — NEHÉZ, egyenlő osztás =====`);
    {
      const p = await open(b);
      const { banner, state } = await play(p, game, 'hard', { Sere: 3, Kecsi: 3 });
      const sere = state.find(x => x.n === 'Sere'), kecsi = state.find(x => x.n === 'Kecsi');
      ok(sere.d === 3 && kecsi.d === 3, 'mindkettő 3 korty (nem 9)', sere.d + '/' + kecsi.d);
      ok(/3\s*KORTY/i.test(banner), 'egyenlőnél a banner „3 KORTY" metrikát mutat', (banner.match(/\d+\s*KORTY/i) || ['nincs'])[0]);
      ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
      await p.close();
    }
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})();
