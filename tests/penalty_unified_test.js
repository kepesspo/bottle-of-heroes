// v10.271 — EGY büntetés-függvény, és a korty-szám átmegy a bannerbe
// v10.272 — EGY büntetés-FELÜLET is: modal, soronként `− szám +`
//
// Amit ellenőriz:
//   1. AZONOS összeg → a banner KIÍRJA a korty-számot (ez volt a hiba)
//   2. a nehézségi szorzó NEM szorozza fel a büntetést (extrémen is 2 = 2)
//   3. eltérő összegnél marad a névenkénti felsorolás, szám nélkül
//   4. a wildcard „Szabályszegő?" UGYANAZT a modalt nyitja, `− szám +` sorokkal
//   5. a wildcard-büntetés mostantól 1-nél TÖBB kortyot és TÖBB embert is tud
//      (korábban fix 1 korty ment egyetlen embernek)
//   6. „Fordított kör" wildcard alatt a büntetés NEM fordul meg
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

// ── A NYITOTT büntetés-modal vezerlese. v10.272 ota UGYANAZ a modal jon a
//    MENÜ-bol es a wildcardbol, tehat egyetlen helper eleg mindkettohoz.
//
//    FIGYELEM: a hatterben futo jatek IS kirajzolhat korty-kiosztot (a
//    Ko-papir-ollo "1. kör — kortyok" lapjat), sajat "korty kiosztva" gombbal.
//    Ezert NEM eleg a gombra keresni — a PenaltyModal sajat overlay-jere
//    (zIndex 60) szukitunk, kulonben a hatter lapjat vezerelnenk.
const findCard = () => {
  const ov = [...document.querySelectorAll('div')].filter(d => d.style && d.style.zIndex === '60')
    .find(d => [...d.querySelectorAll('button')].some(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || '')));
  return ov ? ov.firstElementChild : null;
};
const modalInfo = p => p.evaluate(() => {
  const card = window.__findCard();
  if (!card) return null;
  const btn = [...card.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || ''));
  const rows = [...card.querySelectorAll('div')].filter(d =>
    [...d.querySelectorAll(':scope > div > button')].length === 2);
  return {
    cim: (card.querySelector('div') || {}).innerText || '',
    // kozepre igazitott MODAL-e (nem also lap): a kartya nem er le a kepernyo aljara
    modal: Math.abs(card.getBoundingClientRect().bottom - window.innerHeight) > 20,
    szelesseg: Math.round(card.getBoundingClientRect().width),
    minusz: [...card.querySelectorAll('button')].filter(x => (x.textContent || '').trim() === '−').length,
    plusz: [...card.querySelectorAll('button')].filter(x => (x.textContent || '').trim() === '+').length,
    zaroGomb: btn.innerText.trim(),
  };
});

const assignInModal = (p, assign) => p.evaluate((assign) => {
  const card = window.__findCard();
  if (!card) return 'nincs modal';
  for (const [name, n] of Object.entries(assign)) {
    const lbl = [...card.querySelectorAll('div')].find(d => (d.textContent || '').trim() === name && d.children.length === 0);
    if (!lbl) return 'nincs cimke: ' + name;
    const row = lbl.parentElement;
    const plus = [...row.querySelectorAll('button')].find(x => (x.textContent || '').trim() === '+');
    if (!plus) return 'nincs + gomb: ' + name;
    for (let i = 0; i < n; i++) plus.click();
  }
  return 'ok';
}, assign);

const confirmModal = async (p) => {
  await p.evaluate(() => {
    const card = window.__findCard();
    const btn = card && [...card.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || ''));
    if (btn) btn.click();
  });
  await p.waitForTimeout(1000);
};

async function openMenuPenalty(p) {
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /MENÜ/i.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(900);
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => (x.innerText || '').trim() === 'Büntetés'); if (b) b.click(); });
  await p.waitForTimeout(900);
}
async function openWcPenalty(p) {
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /Szabályszegő/.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(800);
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
  await p.evaluate('window.__findCard = ' + findCard.toString());

  console.log('\n===== 1. AZONOS ÖSSZEG → A BANNER KIÍRJA A SZÁMOT =====');
  // EXTRÉM nehezseg (×5) — pont ez a csapda: az onResult minden mas korty-szamot
  // beszoroz, tehat ha a buntetes nem lenne "abszolut", itt 10 KORTY jonne ki.
  await mount(p, { diff: 'extreme' });
  await openMenuPenalty(p);
  const m1 = await modalInfo(p);
  ok(m1 !== null, 'megnyílik a büntetés-modal');
  ok(m1 && m1.modal, 'KÖZÉPRE igazított modal, nem alsó lap (v10.272)');
  ok(m1 && m1.minusz === 3 && m1.plusz === 3, 'minden sorban ott a − és a + (3 játékos)',
     m1 && (m1.minusz + '× − / ' + m1.plusz + '× +'));
  ok(await assignInModal(p, { Sere: 2, Kecsi: 2 }) === 'ok', 'a léptetővel kiosztható');
  await confirmModal(p);
  const st1 = await drinksOf(p);
  const b1 = await bannerText(p);
  ok(st1 === 'Sere:2,Kecsi:2,Vivi:0', 'a korty pontosan annyi, amennyit kiosztottunk', st1);
  ok(/2 KORTY/i.test(b1), 'a banner KIÍRJA a korty-számot (ez volt a hiba)', (b1.match(/\d+ KORTY/i) || ['nincs szám'])[0]);
  ok(!/10 KORTY/i.test(b1), 'az EXTRÉM ×5 NEM szorozza fel a büntetést', b1.slice(0, 60));
  ok(/ISZNAK|ISZIK/i.test(b1), 'a szabályszegők a vesztes oldalon állnak');

  console.log('\n===== 2. ELTÉRŐ ÖSSZEG → NÉVENKÉNTI FELSOROLÁS =====');
  await mount(p, { diff: 'mid' });
  await openMenuPenalty(p);
  ok(await assignInModal(p, { Sere: 2, Kecsi: 1 }) === 'ok', 'a léptetővel kiosztható');
  await confirmModal(p);
  const st2 = await drinksOf(p);
  const b2 = await bannerText(p);
  ok(st2 === 'Sere:2,Kecsi:1,Vivi:0', 'a korty fejenként pontos', st2);
  ok(/Sere 2/.test(b2) && /Kecsi 1/.test(b2), 'a banner névenként sorolja fel', (b2.match(/Sere \d.{0,20}/) || ['nincs'])[0]);
  ok(!/\d+ KORTY/i.test(b2), 'és NEM ír ki egyetlen számot — egyik sem lenne igaz',
     (b2.match(/\d+ KORTY/i) || ['nincs szám'])[0]);

  console.log('\n===== 3. WILDCARD „SZABÁLYSZEGŐ?" — UGYANAZ A MODAL =====');
  await mount(p, { diff: 'extreme', wcEffect: 'double' });
  ok(await p.evaluate(() => /Szabályszegő/.test(document.body.innerText || '')), 'aktív wildcard, ott a „Szabályszegő?" gomb');
  await openWcPenalty(p);
  const m3 = await modalInfo(p);
  ok(m3 !== null, 'megnyílik a szabályszegő-modal');
  ok(await p.evaluate(() => /Ki szegte meg a szabályt/.test(document.body.innerText || '')), 'a címe „Ki szegte meg a szabályt?"');
  ok(m3 && m3.minusz === 3 && m3.plusz === 3, 'ITT IS ott a − és a + minden soron (korábban csak korsó-ikon volt)',
     m3 && (m3.minusz + '× − / ' + m3.plusz + '× +'));
  ok(m3 && m1 && m3.szelesseg === m1.szelesseg, 'a két modal ugyanolyan széles — egy felület',
     m3 && (m3.szelesseg + ' px vs ' + m1.szelesseg + ' px'));
  ok(await assignInModal(p, { Kecsi: 1 }) === 'ok', 'a szabályszegő megjelölhető');
  await confirmModal(p);
  const st3 = await drinksOf(p);
  const b3 = await bannerText(p);
  ok(st3 === 'Sere:0,Kecsi:1,Vivi:0', 'a szabályszegő pontosan 1 kortyot kap', st3);
  ok(/1 KORTY/i.test(b3), 'a result banner kiírja az 1 kortyot', (b3.match(/\d+ KORTY/i) || ['nincs'])[0]);
  ok(!/5 KORTY|10 KORTY/i.test(b3), 'a dupla wildcard + extrém sem szorozza fel', b3.slice(0, 60));
  ok(/Kecsi/.test(b3), 'a bannerben a szabályszegő neve áll');
  ok(await p.evaluate(() => !/iszik 1-et!/.test(document.body.innerText || '')), 'nincs többé külön Toast');

  console.log('\n===== 4. ÚJ KÉPESSÉG: TÖBB KORTY, TÖBB EMBER =====');
  // Korabban a wildcard-buntetes FIX 1 korty volt EGYETLEN embernek.
  await mount(p, { diff: 'mid', wcEffect: 'double' });
  await openWcPenalty(p);
  ok(await assignInModal(p, { Sere: 3, Vivi: 2 }) === 'ok', 'a szabályszegésért több korty is adható');
  await confirmModal(p);
  const st4 = await drinksOf(p);
  const b4 = await bannerText(p);
  ok(st4 === 'Sere:3,Kecsi:0,Vivi:2', 'két embernek, eltérő összeggel — ez korábban lehetetlen volt', st4);
  ok(/Sere 3/.test(b4) && /Vivi 2/.test(b4), 'a banner mindkettőt felsorolja', (b4.match(/Sere \d.{0,20}/) || ['nincs'])[0]);

  console.log('\n===== 5. „FORDÍTOTT KÖR" ALATT A BÜNTETÉS NEM FORDUL MEG =====');
  await mount(p, { diff: 'mid', wcEffect: 'reverse' });
  ok(await p.evaluate(() => /Fordított kör/.test(document.body.innerText || '')), 'aktív a fordított kör wildcard');
  await openWcPenalty(p);
  ok(await assignInModal(p, { Sere: 1 }) === 'ok', 'a szabályszegő megjelölhető');
  await confirmModal(p);
  const st5 = await drinksOf(p);
  const b5 = await bannerText(p);
  ok(st5 === 'Sere:1,Kecsi:0,Vivi:0', 'a szabályszegő iszik, nem pontot kap', st5);
  ok(/ISZIK|ISZNAK/i.test(b5), 'a bannerben is a vesztes oldalon áll', b5.slice(0, 50));
  ok(!/NYERTES/i.test(b5), 'NEM lett belőle nyertes a fordított kör miatt', b5.slice(0, 60));

  console.log('\n===== 6. MÉGSE — NEM OSZT KI SEMMIT =====');
  await mount(p, { diff: 'mid' });
  await openMenuPenalty(p);
  await assignInModal(p, { Sere: 2 });
  await p.evaluate(() => {
    const card = window.__findCard();
    const btn = card && [...card.querySelectorAll('button')].find(x => (x.innerText || '').trim() === 'Mégse');
    if (btn) btn.click();
  });
  await p.waitForTimeout(700);
  ok(await drinksOf(p) === 'Sere:0,Kecsi:0,Vivi:0', 'a Mégse után egy korty sem került ki',
     await drinksOf(p));
  ok(await modalInfo(p) === null, 'és a modal bezárult');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
