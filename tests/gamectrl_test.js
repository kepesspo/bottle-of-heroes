// v10.308 — MENÜ → Vezérlés panel elrendezése
//
// A panel felépítése fentről lefelé:
//   vezető-fejléc → szobakód-kártya → NÉGY gomb EGY sorban →
//   „Játékos hozzáadása" (teljes szélesség) → Kilépés
//
// Amit ellenőriz, és ami korábban másképp volt:
//   1. a négy gomb EGY sorban van (nem 2×2 rács), egyforma magasan
//   2. a szobakód sorában NINCS apró „+" — a játékos-hozzáadás lent, teljes
//      szélességben áll, ONLINE és OFFLINE partiban ugyanúgy
//   3. a sorrend: gombok ELŐBB, „Játékos hozzáadása" UTÁNA
//   4. a Kilépés nem tömör sáv, hanem szöveges gomb (átlátszó háttér)
//   5. a négy gombnak KÜLÖN háttere van — a „Vissza" (letiltott) nem
//      olvadhat egybe az „Újra"-val
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

async function nyisdMegAVezerlest(p, roomCode) {
  // A menu-lap PORTALBA rendereel (nem a `#__p`-be), ezert a `#__p` torlese
  // nem takaritja el az elozo panelt — ujratoltunk, kulonben a masodik eset
  // mindket panel gombjait latna (8 gomb, es a merések osszekeverednek).
  await p.reload({ waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2800);
  await p.evaluate((rc) => {
    const old = document.getElementById('__p'); if (old) old.remove();
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const nev = ['Sere', 'Kecsi', 'Luca', 'Dani'];
    function H() {
      const [players, setPlayers] = React.useState(nev.map((x, i) => ({
        id: 'p' + i, name: x, color: ['#E0655F','#4FC2A0','#5BA0DB','#F5C842'][i],
        points: i === 0 ? 3 : 0, drinks: 0 })));
      return React.createElement(PlayScreen, {
        go: () => {}, players, setPlayers, selectedGames: ['reakcio'], roomCode: rc,
        setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
        gameMeta: { modes: ['points'], difficulty: 'easy' },
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  }, roomCode);
  await p.waitForTimeout(2600);
  // a jatek sajat nyito-lapja utban lenne
  await p.evaluate(() => { const pop = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '9998'); if (pop) pop.click(); });
  await p.waitForTimeout(500);
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /MENÜ/.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(800);
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /^Vezérlés$/.test((x.innerText || '').trim())); if (b) b.click(); });
  await p.waitForTimeout(900);
}

const olvas = p => p.evaluate(() => {
  const btns = [...document.querySelectorAll('button')];
  const NEV = /^(Büntetés|Vissza|Újra|Következő)$/;
  const akcio = btns
    .filter(x => NEV.test((x.innerText || '').trim()))
    .map(x => { const r = x.getBoundingClientRect();
      return { n: (x.innerText || '').trim(), y: Math.round(r.top), h: Math.round(r.height),
               bg: getComputedStyle(x).backgroundColor }; });
  const add = btns.find(x => /Játékos hozzáadása/.test(x.innerText || ''));
  const kilep = btns.find(x => /Kilépés/.test(x.innerText || ''));
  return {
    akcio,
    aproPlusz: btns.filter(x => x.title === 'Játékos hozzáadása').length,
    addW: add ? Math.round(add.getBoundingClientRect().width) : null,
    addY: add ? Math.round(add.getBoundingClientRect().top) : null,
    kilepBg: kilep ? getComputedStyle(kilep).backgroundColor : null,
    kilepY: kilep ? Math.round(kilep.getBoundingClientRect().top) : null,
    panelW: Math.round((document.querySelector('#__p') || document.body).getBoundingClientRect().width),
  };
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 920 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3000);

  for (const [cimke, kod] of [['ONLINE', '457434'], ['OFFLINE', null]]) {
    console.log('\n===== ' + cimke + ' PARTI =====');
    await nyisdMegAVezerlest(p, kod);
    const r = await olvas(p);

    ok(r.akcio.length === 4, 'megvan mind a négy vezérlő gomb',
       r.akcio.map(x => x.n).join(', ') || 'egy sincs');
    ok(r.akcio.length === 4 && new Set(r.akcio.map(x => x.y)).size === 1,
       'EGY sorban vannak (nem 2×2 rács)', r.akcio.map(x => 'y=' + x.y).join(' '));
    ok(r.akcio.length === 4 && new Set(r.akcio.map(x => x.h)).size === 1,
       'és egyforma magasak', [...new Set(r.akcio.map(x => x.h))].join('/') + ' px');
    // Negy KULON hatter: a "Vissza" letiltott allapota nem olvadhat egybe az
    // "Ujra"-val — korabban mindketto ugyanaz a semleges szurke volt.
    ok(new Set(r.akcio.map(x => x.bg)).size === 4,
       'mind a négynek külön háttere van', r.akcio.map(x => x.n + ':' + x.bg).join(' · '));

    ok(r.aproPlusz === 0, 'a szobakód sorában NINCS apró „+" gomb', r.aproPlusz + ' db');
    ok(r.addW !== null && r.addW > r.panelW * 0.8,
       '„Játékos hozzáadása" teljes szélességű', r.addW + ' / ' + r.panelW + ' px');
    ok(r.addY !== null && r.akcio.length === 4 && r.addY > r.akcio[0].y,
       'a gombsor UTÁN áll', 'gombok y=' + (r.akcio[0] || {}).y + ', hozzáadás y=' + r.addY);
    ok(r.kilepY !== null && r.addY !== null && r.kilepY > r.addY,
       'a Kilépés van legalul', 'kilépés y=' + r.kilepY);
    ok(r.kilepBg === 'rgba(0, 0, 0, 0)',
       'a Kilépés szöveges gomb (nem tömör sáv)', r.kilepBg);
  }

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
