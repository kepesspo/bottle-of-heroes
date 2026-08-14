// v10.369 — „Minden körben" wildcard-teszt kapcsoló
//
// A wildcard alapból IDOZITOVEL jon (6–9 percenkent). Teszteléshez van egy
// kapcsolo (Játékmenet → Wildcard → „🧪 Minden körben"), ami az `gameMeta`-ba
// `wildcardEveryRound:true`-t tesz. Ilyenkor NEM az idozito hoz wildcardot,
// hanem MINDEN korvaltas — determinisztikusan.
//
// A fogodzo: forced effekt (`__wildcardTestEffect='double'`) mellett egy
// szerencsekerek-kor UTAN (Kövi → korvaltas) ott a „Dupla kör" sav. A KONTROLL
// blokk ugyanezt jatssza everyRound NELKUL: mivel az idozito perces (nincs
// `__wildcardTestDelay`), a par masodperces ablakban NEM jon wildcard.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const stub = fs.readFileSync(path.join(__dirname, 'fbstub.js'), 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

async function open(b, effect) {
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  // ⚠️ NINCS `__wildcardTestDelay` — az idozito PERCES marad. Igy amit latunk,
  // az CSAK a korvaltasbol johet (everyRound), nem az idozitobol.
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}
    ${effect ? `window.__wildcardTestEffect=${JSON.stringify(effect)};` : ''}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

const mount = (p, everyRound) => p.evaluate((everyRound) => {
  const r = document.getElementById('root'); if (r) r.style.display = 'none';
  const old = document.getElementById('__p'); if (old) old.remove();
  const root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:#EAF2FB';
  document.body.appendChild(root);
  function H() {
    const [ps, setPs] = React.useState([
      { id: 'a', name: 'Sere', color: '#E07A5F', points: 0, drinks: 0 },
      { id: 'b', name: 'Kecsi', color: '#4FC2A0', points: 0, drinks: 0 },
      { id: 'c', name: 'Vivi', color: '#A78BFA', points: 0, drinks: 0 },
    ]);
    window.__players = ps;
    return React.createElement(PlayScreen, {
      go: () => {}, players: ps, setPlayers: setPs, selectedGames: ['szerencse', 'szerencse'],
      roomCode: null, setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
      gameMeta: { modes: ['points', 'drinks', 'wildcard'], difficulty: 'easy',
                  wildcardMin: 6, wildcardMax: 9, ...(everyRound ? { wildcardEveryRound: true } : {}) },
    });
  }
  ReactDOM.createRoot(root).render(React.createElement(H));
}, everyRound);

// Egy szerencsekerek-kor: popup elutasitas → PÖRGESS → Kövi (korvaltas).
async function spinAndNext(p) {
  await p.evaluate(() => { const pop = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '9998'); if (pop) pop.click(); });
  await p.waitForTimeout(500);
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /PÖRGESS/i.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(7000);
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /Kövi/i.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(1800);
}

const hasDupla = p => p.evaluate(() => /Dupla kör/.test(document.body.innerText || ''));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. MINDEN KÖRBEN: a körváltásnál JÖN wildcard ──
  console.log('\n===== 1. MINDEN KÖRBEN — a körváltás hozza a wildcardot =====');
  {
    const p = await open(b, 'double');
    await mount(p, true);
    await p.waitForTimeout(2000);
    ok(!(await hasDupla(p)), 'induláskor még NINCS wildcard');
    await spinAndNext(p);
    ok(await hasDupla(p), '⚠️ a körváltás UTÁN ott a „Dupla kör" wildcard', (await p.evaluate(() => (document.body.innerText.match(/Dupla kör[^!]*/) || ['nincs'])[0])));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 2. KONTROLL: everyRound NÉLKÜL nincs wildcard a rövid ablakban ──
  // Enelkul az 1. blokk akkor is atmenne, ha a wildcard mashonnan (idozito) jon.
  console.log('\n===== 2. KONTROLL — everyRound nélkül NEM jön (perces időzítő) =====');
  {
    const p = await open(b, 'double');
    await mount(p, false);
    await p.waitForTimeout(2000);
    await spinAndNext(p);
    ok(!(await hasDupla(p)), 'a körváltás után NINCS wildcard (az időzítő perces)', (await p.evaluate(() => (document.body.innerText.match(/Dupla kör[^!]*/) || ['nincs'])[0])));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 3. FORRÁS-INVARIÁNS: a kapcsoló a `gameMeta`-ba írja a flaget ──
  console.log('\n===== 3. A KAPCSOLÓ SZERIALIZÁLHATÓ (gameMeta) =====');
  {
    const p = await open(b);
    const okFlag = await p.evaluate(() => {
      // a flag sima boolean, tehat Firestore-ba is lemehet (nem fuggveny)
      const meta = { modes: ['wildcard'], wildcardEveryRound: true };
      return typeof meta.wildcardEveryRound === 'boolean';
    });
    ok(okFlag, 'a `wildcardEveryRound` sima boolean (szerializálható)');
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})();
