// v10.363 — Licit-wildcard (a Csendes árverés beolvadt a wildcardba)
//
// A kulonallo „Csendes arveres" JATEK megszunt; a licit-mechanika egy WILDCARD
// lett (`effect:'auction'`). A wildcard-idozito sorsolja, a nyertes egy TARTOS
// szemelyes nyeremeny-savot kap (`activePrizes`), amit kezzel lehet
// „Felhasznalva"-ra allitani — igy a nyeremeny NEM felejtodik el.
//
// Harom fogodzo:
//  1) FORRAS-INVARIANSOK — az auction-wildcard letezik, az arveres JATEK eltunt.
//  2) A LICIT-KONTRAKTUS — az `AuctionOverlay` a legmagasabb licitet adja vissza
//     `onFinish`-en (nyertes + top), a felfedesen ott a „NYERT" jelzo.
//  3) INTEGRACIO — a wildcard tuzelesekor az overlay kinyilik (SOLO jatekon
//     rogton), a „Bezar" utan a nyertes ISSZA a licitet (nehezseggel szorozva),
//     es megjelenik a tartos nyeremeny-sav, amit a „Felhasznalva" gomb kivesz.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'a', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
            { id:'b', name:'Luca', color:'#4FC2A0', points:0, drinks:0 }];

async function open(b, effect) {
  const p = await b.newPage({ viewport: { width: 402, height: 1000 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}
    ${effect ? `window.__wildcardTestEffect=${JSON.stringify(effect)}; window.__wildcardTestDelay=400;` : ''}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

const tap = (p, re) => p.evaluate(r => {
  const b = [...document.querySelectorAll('#__p button')].find(x => new RegExp(r).test(x.textContent || ''));
  if (!b) return false; b.click(); return true;
}, re.source);
const txt = p => p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));
const step = (p, more) => p.evaluate(lab => {
  const b = document.querySelector('#__p button[aria-label="' + lab + '"]');
  if (!b) return false; b.click(); return true;
}, more ? 'Egy korttyal több' : 'Egy korttyal kevesebb');

// Vegigviszi a korbeadós licitet. `list` = licit jatekosonkent, sorrendben.
// A vegen a felfedesen allunk (a „Bezar" gombot a hivo nyomja).
async function bid(p, list) {
  await tap(p, /Licitálás indul/); await p.waitForTimeout(400);
  for (let i = 0; i < list.length; i++) {
    await tap(p, /Én vagyok/); await p.waitForTimeout(300);
    for (let k = 0; k < list[i]; k++) { await step(p, true); await p.waitForTimeout(90); }
    await tap(p, /^Kész|^Következő/); await p.waitForTimeout(400);
  }
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. FORRAS-INVARIANSOK ──
  console.log('\n===== 1. FORRAS: auction-wildcard van, arveres JATEK nincs =====');
  {
    const p = await open(b);
    const inv = await p.evaluate(() => ({
      wcAuction: WILDCARDS.some(w => w.effect === 'auction'),
      noGame:    !GAMES.some(g => g.id === 'arveres'),
      noScenario: !('arveres' in SCENARIOS),
      overlay:   typeof AuctionOverlay === 'function',
      prizes:    Array.isArray(ARVERES_DIJAK) && ARVERES_DIJAK.length >= 8,
    }));
    ok(inv.wcAuction, 'a WILDCARDS tartalmaz `effect:\'auction\'`-t');
    ok(inv.noGame, '⚠️ az `arveres` mint JATEK eltűnt a GAMES-ből');
    ok(inv.noScenario, 'és a SCENARIOS-ból is');
    ok(inv.overlay, 'az `AuctionOverlay` komponens létezik');
    ok(inv.prizes, 'a nyeremény-bank (ARVERES_DIJAK) megmaradt', (await p.evaluate(()=>ARVERES_DIJAK.length)));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 2. A LICIT-KONTRAKTUS (AuctionOverlay) ──
  // A legmagasabb licit nyer; az `onFinish` a nyertest ES a licitet adja vissza.
  console.log('\n===== 2. AUCTIONOVERLAY — a legmagasabb licit nyer =====');
  {
    const p = await open(b);
    await p.evaluate((pl) => {
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const root = document.createElement('div'); root.id = '__p';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto';
      document.body.appendChild(root);
      window.__res = null;
      ReactDOM.createRoot(root).render(React.createElement(AuctionOverlay, {
        players: pl, prize: 'TESZT-DÍJ', drinkMult: 1,
        onFinish: (r) => { window.__res = { top: r.top, win: r.winners.map(x => x.name), prize: r.prize }; },
      }));
    }, PL);
    await p.waitForTimeout(300);
    await bid(p, [2, 5]);              // Sere 2, Luca 5 → Luca nyer, top 5
    const rev = await txt(p);
    ok(/NYERT/.test(rev), 'a felfedésen ott a „NYERT" jelző', rev.slice(0, 40));
    ok(/TESZT-DÍJ/.test(rev), 'és a nyeremény szövege', /TESZT-DÍJ/.test(rev));
    await tap(p, /^Bezár/); await p.waitForTimeout(200);
    const res = await p.evaluate(() => window.__res);
    ok(!!res, 'az `onFinish` lefutott');
    ok(res && res.top === 5, 'a licit a legmagasabb (5)', res && res.top);
    ok(res && res.win.length === 1 && res.win[0] === 'Luca', 'és a nyertes a legtöbbet ígérő (Luca)', res && res.win.join(','));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 3. INTEGRACIO: a wildcard nyit, a nyertes iszik, a sav megjelenik ──
  // SOLO jatekon (Busz) a licit-wildcard AZONNAL nyit (nincs atmenet, amire
  // varni). A `finishAuction` konyvel es felteszi a tartos nyeremeny-savot.
  console.log('\n===== 3. INTEGRACIO — nyit, könyvel, tartós sáv =====');
  for (const [diff, mult] of [['easy', 1], ['hard', 3]]) {
    const p = await open(b, 'auction');
    await p.evaluate(({ pl, diff }) => {
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const root = document.createElement('div'); root.id = '__p';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
      document.body.appendChild(root);
      function H() {
        const [ps, setPs] = React.useState(pl); window.__players = ps;
        return React.createElement(PlayScreen, { go:()=>{}, players:ps, setPlayers:setPs,
          selectedGames:['busz'], roomCode:null,
          gameMeta:{ modes:['points','drinks','wildcard'], difficulty:diff, wildcardMin:1, wildcardMax:1 },
          setGameMeta:()=>{}, setScoreHistory:()=>{}, setLastGameRound:()=>{} });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    }, { pl: PL, diff });
    // varjuk, hogy a wildcard-idozito (400ms) kinyissa az overlayt
    await p.waitForFunction(() => /Licitálás indul/.test(document.getElementById('__p')?.innerText || ''), { timeout: 4000 }).catch(() => {});
    const opened = await p.evaluate(() => /Licitálás indul/.test(document.getElementById('__p')?.innerText || ''));
    ok(opened, `[${diff}] a licit-wildcard AZONNAL megnyitja az overlayt`);
    await bid(p, [3, 1]);             // Sere 3, Luca 1 → Sere nyer, top 3
    await tap(p, /^Bezár/); await p.waitForTimeout(400);
    const st = await p.evaluate(() => (window.__players || []).map(x => ({ n:x.name, dr:x.drinks })));
    const sere = st.find(x => x.n === 'Sere');
    ok(sere && sere.dr === 3 * mult, `[${diff}] a nyertes issza a licitet × nehézség (${3 * mult})`, sere && sere.dr);
    const t = await txt(p);
    ok(/🎁/.test(t) && /Sere/.test(t), `[${diff}] megjelent a tartós nyeremény-sáv`, /🎁/.test(t));
    // „Felhasznalva" → a sav eltunik
    await tap(p, /Felhasználva/); await p.waitForTimeout(300);
    const t2 = await txt(p);
    ok(!/🎁/.test(t2), `[${diff}] a „Felhasználva" kiveszi a sávot`, /🎁/.test(t2));
    ok(p.__errs.length === 0, `[${diff}] nincs JS hiba`, p.__errs.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})();
