// v10.204 — Büntetés = korty-kiosztó, Koccintó kivezetve
//
// Amit ellenoriz:
//   1. a MENÜ-ben nincs tobbe Koccinto
//   2. a Buntetes gomb egy korty-kioszto lapot nyit
//   3. a kiosztott korty tenyleg rakerul a jatekosokra (innen megy a
//      parti vegen a statisztikaba)
//   4. a lap bezarul, es a toast megmondja, ki mennyit kapott
//
// FIGYELEM: a hatterben futo jatek IS kirajzolhat DrinkDistributort
// (pl. Ko-papir-ollo "1. kör — kortyok"), ezert minden kattintast a
// buntetes-lapon BELUL kell keresni.
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

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);

  // PlayScreen kozvetlenul, harom jatekossal
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column';
    document.body.appendChild(root);
    function H() {
      const [players, setPlayers] = React.useState([
        { id: 'a', name: 'Sere', color: '#E07A5F', points: 0, drinks: 0 },
        { id: 'b', name: 'Kecsi', color: '#4FC2A0', points: 0, drinks: 0 },
        { id: 'c', name: 'Vivi', color: '#A78BFA', points: 0, drinks: 0 },
      ]);
      window.__players = players;
      return React.createElement(PlayScreen, {
        go: () => {}, players, setPlayers, selectedGames: ['kopapir'],
        roomCode: null, gameMeta: { modes: ['points'], difficulty: 'mid' }, setGameMeta: () => {},
        setScoreHistory: () => {}, setLastGameRound: () => {},
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(2400);

  console.log('\n===== MENÜ =====');
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /MENÜ/i.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(900);
  const menuTxt = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  ok(!/Koccint/i.test(menuTxt), 'a Koccintó eltűnt a menüből');
  ok(/Büntetés — ki igyon\?/.test(menuTxt), 'a Büntetés gomb korty-kiosztót ígér');

  console.log('\n===== KORTY KIOSZTÁSA =====');
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /Büntetés/i.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(1100);

  const clicked = await p.evaluate(() => {
    const titleEl = [...document.querySelectorAll('*')].find(e => (e.textContent || '').trim() === 'Büntetés — ki igyon?');
    let sheet = titleEl;
    while (sheet && !/Senki sem iszik|korty kiosztva/.test(sheet.textContent || '')) sheet = sheet.parentElement;
    if (!sheet) return 'nincs lap';
    window.__sheet = sheet;
    const plus = (name, n) => {
      const lbl = [...sheet.querySelectorAll('div')].find(d => (d.textContent || '').trim() === name && d.children.length === 0);
      if (!lbl) return 'nincs címke: ' + name;
      let row = lbl.parentElement;
      while (row && row.querySelectorAll('button').length < 2) row = row.parentElement;
      if (!row) return 'nincs sor: ' + name;
      const btn = [...row.querySelectorAll('button')].find(x => (x.textContent || '').trim() === '+');
      if (!btn) return 'nincs + gomb: ' + name;
      for (let i = 0; i < n; i++) btn.click();
      return name + ' OK';
    };
    return [plus('Sere', 2), plus('Kecsi', 1)].join(' | ');
  });
  ok(clicked === 'Sere OK | Kecsi OK', 'a lapon minden játékos sora kiosztható', clicked);
  await p.waitForTimeout(500);

  const label = await p.evaluate(() => {
    const b = [...window.__sheet.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || ''));
    return b ? b.innerText.trim() : 'nincs';
  });
  ok(/^3 korty kiosztva/.test(label), 'a záró gomb az összeget mutatja', label);

  await p.evaluate(() => { const b = [...window.__sheet.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(900);

  const state = await p.evaluate(() => window.__players.map(x => x.name + ':' + x.drinks).join(','));
  ok(state === 'Sere:2,Kecsi:1,Vivi:0', 'a korty rákerült a játékosokra', state);
  ok(await p.evaluate(() => !document.body.innerText.includes('Büntetés — ki igyon?')), 'a lap bezárult');
  const toast = await p.evaluate(() => { const m = document.body.innerText.match(/Büntetés: [^\n]*/); return m ? m[0].trim() : 'nincs'; });
  ok(/Sere 2/.test(toast) && /Kecsi 1/.test(toast), 'a toast megmondja, ki mennyit kapott', toast);

  const real = errs.filter(e => !/ServiceWorker/.test(e));
  ok(real.length === 0, 'nincs JS hiba', real.join(' | '));

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})();
