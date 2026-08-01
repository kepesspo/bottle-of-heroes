// v10.271 — EGY büntetés-függvény, és a korty-szám átmegy a bannerbe
//
// Amit ellenőriz:
//   1. AZONOS összeg → a banner KIÍRJA a korty-számot (ez volt a hiba: nem írta)
//   2. a nehézségi szorzó NEM szorozza fel a büntetést (extrémen is 2 = 2)
//   3. eltérő összegnél marad a névenkénti felsorolás, szám nélkül
//      (nincs olyan EGY szám, ami igaz lenne)
//   4. a wildcard „Szabályszegő?" UGYANAZT az utat járja: result banner
//      1 kortyval, nem külön Toast
//   5. „Fordított kör" wildcard alatt a büntetés NEM fordul meg
//      (a szabályszegő nem lesz nyertes)
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

// PlayScreen felallitasa. `wcEffect` megadasakor a paklit egyetlen lapra
// szukitjuk, es az EGY darab 60 000 ms-os wildcard-idozitot rovidre zarjuk
// (a konfigbol nem lehet 1 percnel rovidebbre venni). Mas idozito nem hasznal
// pont ennyit, ezert ez biztonsagos.
async function mount(p, { diff, wcEffect }) {
  await p.evaluate(({ diff, wcEffect }) => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const old = document.getElementById('__p'); if (old) old.remove();
    if (window.__restoreWc) { window.__restoreWc(); window.__restoreWc = null; }
    if (wcEffect) {
      const all = WILDCARDS.slice();
      const pick = all.find(w => w.effect === wcEffect);
      WILDCARDS.length = 0; WILDCARDS.push(pick);
      const orig = window.setTimeout;
      window.setTimeout = function (fn, ms) { return orig(fn, ms === 60000 ? 100 : ms); };
      window.__restoreWc = () => {
        WILDCARDS.length = 0; all.forEach(w => WILDCARDS.push(w));
        window.setTimeout = orig;
      };
    }
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:#EAF2FB';
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
        roomCode: null, setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
        gameMeta: { modes: wcEffect ? ['points', 'wildcard'] : ['points'], difficulty: diff || 'mid',
                    ...(wcEffect ? { wildcardMin: 1, wildcardMax: 1 } : {}) },
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  }, { diff, wcEffect });
  await p.waitForTimeout(wcEffect ? 3000 : 2400);
}

// A MENÜ -> Büntetés lapon kiosztunk, majd zarunk.
async function menuPenalty(p, assign) {
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /MENÜ/i.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(900);
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => (x.innerText || '').trim() === 'Büntetés'); if (b) b.click(); });
  await p.waitForTimeout(1100);
  const res = await p.evaluate((assign) => {
    const titleEl = [...document.querySelectorAll('*')].find(e => (e.textContent || '').trim() === 'Büntetés — ki igyon?');
    let sheet = titleEl;
    while (sheet && !/Senki sem iszik|korty kiosztva/.test(sheet.textContent || '')) sheet = sheet.parentElement;
    if (!sheet) return 'nincs lap';
    window.__sheet = sheet;
    for (const [name, n] of Object.entries(assign)) {
      const lbl = [...sheet.querySelectorAll('div')].find(d => (d.textContent || '').trim() === name && d.children.length === 0);
      if (!lbl) return 'nincs cimke: ' + name;
      let row = lbl.parentElement;
      while (row && row.querySelectorAll('button').length < 2) row = row.parentElement;
      const btn = [...row.querySelectorAll('button')].find(x => (x.textContent || '').trim() === '+');
      for (let i = 0; i < n; i++) btn.click();
    }
    return 'ok';
  }, assign);
  if (res !== 'ok') return res;
  await p.waitForTimeout(400);
  await p.evaluate(() => { const b = [...window.__sheet.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(1000);
  return 'ok';
}

const bannerText = p => p.evaluate(() => {
  const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250');
  return el ? (el.innerText || '').replace(/\s+/g, ' ').trim() : '';
});
const drinksOf = p => p.evaluate(() => window.__players.map(x => x.name + ':' + x.drinks).join(','));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);

  console.log('\n===== 1. AZONOS ÖSSZEG → A BANNER KIÍRJA A SZÁMOT =====');
  // EXTRÉM nehezseg (×5) — pont ez a csapda: az onResult minden mas korty-szamot
  // beszoroz, tehat ha a buntetes nem lenne "abszolut", itt 10 KORTY jonne ki.
  await mount(p, { diff: 'extreme' });
  ok(await menuPenalty(p, { Sere: 2, Kecsi: 2 }) === 'ok', 'a büntetés-lap kiosztható');
  const st1 = await drinksOf(p);
  const b1 = await bannerText(p);
  ok(st1 === 'Sere:2,Kecsi:2,Vivi:0', 'a korty pontosan annyi, amennyit kiosztottunk', st1);
  ok(/2 KORTY/i.test(b1), 'a banner KIÍRJA a korty-számot (ez volt a hiba)', (b1.match(/\d+ KORTY/i) || ['nincs szám'])[0]);
  ok(!/10 KORTY/i.test(b1), 'az EXTRÉM ×5 NEM szorozza fel a büntetést', b1.slice(0, 60));
  ok(/ISZNAK|ISZIK/i.test(b1), 'a szabályszegők a vesztes oldalon állnak');

  console.log('\n===== 2. ELTÉRŐ ÖSSZEG → NÉVENKÉNTI FELSOROLÁS =====');
  await mount(p, { diff: 'mid' });
  ok(await menuPenalty(p, { Sere: 2, Kecsi: 1 }) === 'ok', 'a büntetés-lap kiosztható');
  const st2 = await drinksOf(p);
  const b2 = await bannerText(p);
  ok(st2 === 'Sere:2,Kecsi:1,Vivi:0', 'a korty fejenként pontos', st2);
  ok(/Sere 2/.test(b2) && /Kecsi 1/.test(b2), 'a banner névenként sorolja fel', (b2.match(/Sere \d.{0,20}/) || ['nincs'])[0]);
  ok(!/\d+ KORTY/i.test(b2), 'és NEM ír ki egyetlen számot — egyik sem lenne igaz',
     (b2.match(/\d+ KORTY/i) || ['nincs szám'])[0]);

  console.log('\n===== 3. WILDCARD „SZABÁLYSZEGŐ?" — UGYANAZ AZ ÚT =====');
  await mount(p, { diff: 'extreme', wcEffect: 'double' });
  const wcUp = await p.evaluate(() => /Szabályszegő/.test(document.body.innerText || ''));
  ok(wcUp, 'aktív wildcard, ott a „Szabályszegő?" gomb');
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /Szabályszegő/.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(700);
  ok(await p.evaluate(() => /Ki szegte meg a szabályt/.test(document.body.innerText || '')), 'megnyílik a szabályszegő-választó');
  await p.evaluate(() => {
    const sheet = [...document.querySelectorAll('div')].find(d => /Ki szegte meg a szabályt/.test(d.innerText || '') && d.style && d.style.maxWidth === '340px');
    const btn = [...(sheet || document).querySelectorAll('button')].find(x => /Kecsi/.test(x.innerText || ''));
    if (btn) btn.click();
  });
  await p.waitForTimeout(1000);
  const st3 = await drinksOf(p);
  const b3 = await bannerText(p);
  ok(st3 === 'Sere:0,Kecsi:1,Vivi:0', 'a szabályszegő pontosan 1 kortyot kap', st3);
  ok(b3.length > 0, 'a result banner feljön (korábban csak egy Toast volt)', b3.slice(0, 50));
  ok(/1 KORTY/i.test(b3), 'és kiírja az 1 kortyot', (b3.match(/\d+ KORTY/i) || ['nincs'])[0]);
  ok(!/5 KORTY|10 KORTY/i.test(b3), 'a dupla wildcard + extrém sem szorozza fel', b3.slice(0, 60));
  ok(/Kecsi/.test(b3), 'a bannerben a szabályszegő neve áll', (b3.match(/Kecsi/) || ['nincs'])[0]);
  ok(await p.evaluate(() => !/iszik 1-et!/.test(document.body.innerText || '')), 'nincs többé külön Toast');

  console.log('\n===== 4. „FORDÍTOTT KÖR" ALATT A BÜNTETÉS NEM FORDUL MEG =====');
  await mount(p, { diff: 'mid', wcEffect: 'reverse' });
  ok(await p.evaluate(() => /Fordított kör/.test(document.body.innerText || '')), 'aktív a fordított kör wildcard');
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /Szabályszegő/.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(700);
  await p.evaluate(() => {
    const sheet = [...document.querySelectorAll('div')].find(d => /Ki szegte meg a szabályt/.test(d.innerText || '') && d.style && d.style.maxWidth === '340px');
    const btn = [...(sheet || document).querySelectorAll('button')].find(x => /Sere/.test(x.innerText || ''));
    if (btn) btn.click();
  });
  await p.waitForTimeout(1000);
  const st4 = await drinksOf(p);
  const b4 = await bannerText(p);
  ok(st4 === 'Sere:1,Kecsi:0,Vivi:0', 'a szabályszegő iszik, nem pontot kap', st4);
  ok(/ISZIK|ISZNAK/i.test(b4), 'a bannerben is a vesztes oldalon áll', b4.slice(0, 50));
  ok(!/NYERTES/i.test(b4), 'NEM lett belőle nyertes a fordított kör miatt', b4.slice(0, 60));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
