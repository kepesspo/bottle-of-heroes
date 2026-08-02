// v10.296 — A korty-osztó sorok NEM hazudhatnak: a kiírt szám annyi, amennyit ad
//
// Elozmeny (v10.295): egy kulon `getDrinkMultiplier` szorozta a kijelzest a
// jatek MAGYAR cimkejebol ('kozepes'/'nehez'). Ket baja volt:
//   * a parti nehezsege `gameMeta.difficulty` = 'easy'|'mid'|'hard'|'extreme',
//     tehat a magyar cimkere valo illesztes MINDIG 1-et adott — a funkcio halott
//   * a Buntetes-modalban viszont a jatek sajat cimkejebol 2-3-at kapott, es
//     mivel a buntetes ABSZOLUT, a modal tobbet irt ki, mint amennyit adott
//
// Amit ez a teszt orzi:
//   1. JATEK (En meg soha): a leptetore irt szam = amennyit a jatekos KAP
//      — konnyu 1x, kozepes 2x, nehez 3x, extrem 5x
//   2. BUNTETES: abszolut marad minden szinten (a modal szama = a kapott korty)
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

async function mount(p, diff, game) {
  await p.evaluate(({ diff, game }) => {
    const old = document.getElementById('__p'); if (old) old.remove();
    [...document.body.children].forEach(c => { if (c.id !== '__p') c.style.display = 'none'; });
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const nev = ['Sere', 'Kecsi', 'Luca'];
    function H() {
      const [players, setPlayers] = React.useState(nev.map((x, i) => ({ id: 'p' + i, name: x, color: '#5BA0DB', points: 0, drinks: 0 })));
      window.__players = players;
      return React.createElement(PlayScreen, {
        go: () => {}, players, setPlayers, selectedGames: [game],
        roomCode: null, setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
        gameMeta: { modes: ['points'], difficulty: diff },
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  }, { diff, game });
  await p.waitForTimeout(2600);
  await p.evaluate(() => { const pop = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '9998'); if (pop) pop.click(); });
  await p.waitForTimeout(600);
}

// Egy koppintas a `+`-ra az elso soron, majd a kiirt szam es a zaro gomb szovege
const plusz = async (p, root) => {
  await p.evaluate((sel) => {
    const R = document.querySelector(sel);
    const b = [...R.querySelectorAll('button[aria-label="Egy korttyal több"]')][0];
    if (b) b.click();
  }, root);
  await p.waitForTimeout(320);
};

const olvas = (p, root) => p.evaluate((sel) => {
  const R = document.querySelector(sel);
  const span = [...R.querySelectorAll('span')].find(s => /^\d+$/.test((s.innerText || '').trim()) && s.style.minWidth === '44px');
  const btn = [...R.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik|iszik ·/.test(x.innerText || ''));
  return { sor: span ? (span.innerText || '').trim() : null, gomb: btn ? btn.innerText.trim() : null };
}, root);

const kortyok = p => p.evaluate(() => (window.__players || []).map(x => x.drinks));

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await browser.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);

  console.log('\n===== 1. JÁTÉK: A LÉPTETŐ SZÁMA = AMENNYIT A JÁTÉKOS KAP =====');
  for (const [diff, mult, nev] of [['easy', 1, 'Könnyű'], ['mid', 2, 'Közepes'], ['hard', 3, 'Nehéz'], ['extreme', 5, 'Extrém']]) {
    await p.reload({ waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(2200);
    await mount(p, diff, 'sohanem');
    await plusz(p, '#__p');
    const r = await olvas(p, '#__p');
    ok(r.sor === String(mult), `${nev}: a léptetőn ${mult} áll`, r.sor);
    ok(r.gomb === `1 iszik · ${mult} korty`, `${nev}: a gomb is ${mult} kortyot ígér`, r.gomb);

    // Kiosztas + Kovi -> a tenylegesen konyvelt korty
    await p.evaluate(() => {
      const R = document.getElementById('__p');
      const b = [...R.querySelectorAll('button')].find(x => /iszik ·/.test(x.innerText || ''));
      if (b) b.click();
    });
    await p.waitForTimeout(500);
    await p.evaluate(() => {
      const R = document.getElementById('__p');
      const b = [...R.querySelectorAll('button')].find(x => /Kövi/.test(x.innerText || ''));
      if (b) b.click();
    });
    await p.waitForTimeout(900);
    const d = await kortyok(p);
    ok(d[0] === mult, `${nev}: és PONTOSAN ennyi korty került rá — nem hazudott`, JSON.stringify(d));
  }

  console.log('\n===== 2. BÜNTETÉS: ABSZOLÚT MARAD MINDEN SZINTEN =====');
  for (const [diff, nev] of [['easy', 'Könnyű'], ['hard', 'Nehéz'], ['extreme', 'Extrém']]) {
    await p.reload({ waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(2200);
    await mount(p, diff, 'sohanem');
    // MENÜ -> Büntetés
    await p.evaluate(() => {
      const R = document.getElementById('__p');
      const b = [...R.querySelectorAll('button')].find(x => /MENÜ/.test(x.innerText || ''));
      if (b) b.click();
    });
    await p.waitForTimeout(600);
    await p.evaluate(() => {
      const b = [...document.querySelectorAll('button,div')].find(x => (x.innerText || '').trim() === 'Büntetés');
      if (b) b.click();
    });
    await p.waitForTimeout(700);
    const modal = await p.evaluate(() => {
      const m = [...document.querySelectorAll('div')].find(d => /Büntetés — ki igyon/.test(d.innerText || '') && d.style && d.style.maxWidth === '340px');
      if (m) { m.id = '__modal'; return true; }
      return false;
    });
    ok(modal, `${nev}: megnyílt a büntetés-modal`);
    if (!modal) continue;
    await plusz(p, '#__modal');
    await plusz(p, '#__modal');
    const r = await olvas(p, '#__modal');
    ok(r.sor === '2', `${nev}: két koppintás = 2 (nem szorozva)`, r.sor);
    ok(r.gomb === '2 korty kiosztva', `${nev}: a gomb is 2-t ír`, r.gomb);
    await p.evaluate(() => {
      const m = document.getElementById('__modal');
      const b = [...m.querySelectorAll('button')].find(x => /korty kiosztva/.test(x.innerText || ''));
      if (b) b.click();
    });
    await p.waitForTimeout(800);
    const d = await kortyok(p);
    ok(d[0] === 2, `${nev}: és pontosan 2 korty került rá`, JSON.stringify(d));
  }

  ok(errs.length === 0, 'nincs JS hiba', errs.slice(0, 3).join(' | '));
  console.log(fail ? `\n❌ ${fail} HIBA` : '\n✅ MINDEN ELLENORZES RENDBEN');
  await browser.close();
  process.exit(fail ? 1 : 0);
})();
