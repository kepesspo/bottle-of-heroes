// v10.146 — XP-elszámolás a buli végén + szintlépés-ünneplés
//
// A fő kockázat itt egy sorrendi hiba: a "before" statot a NÖVELMÉNY KIÍRÁSA
// ELŐTT kell beolvasni, különben a mai este XP-je kétszer számolódna bele.
// Ezt külön is ellenőrizzük (a stub naplózza az olvasás/írás sorrendjét).
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

// XP_W = { point:10, round:1, win:50, badge:50 }; xpForLevel(L)=300(L−1)+75(L−1)(L−2)
// 2. szint = 300 XP, 3. = 750, 4. = 1350
const seed = (annaPoints) => `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  window.__fbStore['profiles'] = {
    p_a:{ name:'Anna', color:'#5BA0DB' },
    p_b:{ name:'Bela', color:'#E07A5F' },
  };
  window.__fbStore['stats'] = {
    p_a:{ totalPoints:${annaPoints}, totalRounds:0, totalSessions:1, totalWins:0, totalDrinks:0 },
    p_b:{ totalPoints:0,  totalRounds:0, totalSessions:1, totalWins:0, totalDrinks:0 },
  };
  window.__fbStore['game_stats'] = {};
  window.__fbStore['statEvents'] = {};
  window.__fbStore['gameStatEvents'] = {};
  window.__fbStore['seasons'] = {};
  window.__fbStore['config'] = {};
`;

const mount = (aPts, bPts, rounds) => `
  const root = document.createElement('div'); root.id='__es';
  root.style.cssText='position:fixed;inset:0;background:#F5D89B;overflow:auto;z-index:1';
  document.body.appendChild(root);
  ReactDOM.createRoot(root).render(React.createElement(window.EndScreen, {
    players: [
      { id:'a', name:'Anna', color:'#5BA0DB', profileId:'p_a', points:${aPts}, drinks:4 },
      { id:'b', name:'Bela', color:'#E07A5F', profileId:'p_b', points:${bPts}, drinks:9 },
    ],
    go: ()=>{}, resetGame: ()=>{}, lastRound: ${rounds}, scoreHistory: null,
  }));
`;

// A stub fole huzunk egy naplot: latni akarjuk, hogy a stats OLVASAS a
// stats IRAS elott tortent-e.
const orderProbe = `
  window.__ops = [];
  (function () {
    const wrap = () => {
      if (!window.getAllStats || window.__wrapped) return;
      window.__wrapped = true;
      const gs = window.getAllStats, is = window.incrementStats;
      window.getAllStats = function () { window.__ops.push('read'); return gs.apply(this, arguments); };
      window.incrementStats = function () { window.__ops.push('write'); return is.apply(this, arguments); };
    };
    const iv = setInterval(() => { wrap(); if (window.__wrapped) clearInterval(iv); }, 30);
  })();
`;

async function open(b, annaPoints, aPts, bPts, rounds) {
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed(annaPoints));
  await p.addInitScript(orderProbe);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  await p.evaluate(mount(aPts, bPts, rounds));
  await p.waitForTimeout(1600);
  p.__errs = errs;
  return p;
}
const txt = (p) => p.evaluate(() => document.getElementById('__es').innerText.replace(/\n/g, ' | '));
const sheet = (p) => p.evaluate(() => {
  const d = Array.from(document.querySelectorAll('div')).find(x => /SZINTLÉPÉS/i.test(x.innerText || '') && x.style.borderRadius === '28px');
  return d ? d.innerText.replace(/\n/g, ' | ') : null;
});

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── Nincs szintlépés: kis parti, Anna 0 XP-rol indul ─────────────────────
  // Anna (gyoztes): 5 pont·10 + 4 kor·1 + gyozelem 50 + „Elso siker" jelveny 50 = 154 XP
  //   (a gyozelem az elso, ezert a wins-csalad 1. fokozata is teljesul: +1·50 XP)
  // Bela: 1 pont·10 + 4 kor·1 = 14 XP  → egyik sem eri el a 2. szint 300 XP-jet
  console.log('===== XP ELSZAMOLAS, SZINTLEPES NELKUL =====');
  let p = await open(b, 0, 5, 1, 4);
  let t = await txt(p);
  ok('megjelenik a "Szintek — a mai estéből" kártya', /SZINTEK — A MAI ESTÉBŐL/i.test(t), (t.match(/SZINTEK[^|]*/i) || ['NINCS'])[0]);
  ok('Anna XP-je pontosan +154 (5·10 + 4·1 + 50 győzelem + 50 jelvény)', /\+154 \| XP/.test(t), (t.match(/\+\d+ \| XP/g) || []).join(' '));
  ok('Bela XP-je pontosan +14 (1·10 + 4·1, nincs győzelem és jelvény)', /\+14 \| XP/.test(t), (t.match(/\+\d+ \| XP/g) || []).join(' '));
  ok('nincs SZINTLÉPÉS jelölés', !/SZINTLÉPÉS/i.test(t));
  ok('nem ugrik fel az ünneplő modal', (await sheet(p)) === null);
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));

  // ── Sorrend: olvasas ELOTT az iras ─────────────────────────────────────
  const ops = await p.evaluate(() => window.__ops);
  ok('a stat OLVASÁS megelőzi a KIÍRÁST (különben duplán számolna)',
     ops.indexOf('read') >= 0 && ops.indexOf('read') < ops.indexOf('write'), JSON.stringify(ops));

  // ── A kiiras tenylegesen megtortent ────────────────────────────────────
  const stored = await p.evaluate(() => window.__fbStore['stats']);
  ok('a novelmeny kikerult a statba (Anna 5 pont)', (stored.p_a || {}).totalPoints === 5, JSON.stringify(stored.p_a));
  ok('a gyoztes gyozelme is (Anna totalWins=1)', (stored.p_a || {}).totalWins === 1, JSON.stringify(stored.p_a));
  await p.screenshot({ path: __dirname + '/levelup_xp_card.png', fullPage: true });
  await p.close();

  // ── Szintlepes: Anna 290 XP-nel all (29 pont), a +312 atviszi a 300-on ──
  // 20 pont·10 + 12 kor·1 + 50 gyozelem + 50 „Elso siker" jelveny = 312
  console.log('\n===== SZINTLEPES =====');
  p = await open(b, 29, 20, 3, 12);   // 290 XP + 312 = 602 XP → 2. szint (300 XP-tol)
  t = await txt(p);
  ok('a soron ott a SZINTLÉPÉS jelölés', /SZINTLÉPÉS/i.test(t), (t.match(/Anna[^|]*\|[^|]*/) || ['?'])[0]);
  const sh = await sheet(p);
  ok('felugrik az ünneplő modal', !!sh, sh);
  ok('a nevet és az új szintet is kiírja', sh && /Anna/.test(sh) && /2\. szint/.test(sh), sh);
  ok('a szintlépés irányát mutatja (1. → 2.)', sh && /1\..*→ 2\. szint/.test(sh), sh);
  ok('a szerzett XP-t is (+312)', sh && /\+312/.test(sh), sh);
  ok('csak Anna van benne, Bela nem lépett szintet', sh && !/Bela/.test(sh), sh);
  const geo = await p.evaluate(() => {
    const d = Array.from(document.querySelectorAll('div')).find(x => /SZINTLÉPÉS/i.test(x.innerText || '') && x.style.borderRadius === '28px');
    if (!d) return null;
    const r = d.getBoundingClientRect();
    return { w: Math.round(r.width), centered: Math.abs((r.left + r.right) / 2 - 195) < 3, inView: r.top >= 0 && r.bottom <= 900 };
  });
  ok('középre igazított, nem lóg ki', geo && geo.centered && geo.w <= 380 && geo.inView, JSON.stringify(geo));
  await p.screenshot({ path: __dirname + '/levelup_sheet.png', fullPage: true });

  // bezarhato, es utana a kartya tovabbra is ott van
  await p.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(x => /^Tovább$/.test((x.innerText || '').trim()));
    if (btn) btn.click();
  });
  await p.waitForTimeout(500);
  ok('a "Tovább" bezárja', (await sheet(p)) === null);
  ok('a bezárás után is ott az XP-kártya', /SZINTEK — A MAI ESTÉBŐL/i.test(await txt(p)));
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.close();

  // ── A SZINT SOSEM MEHET LEFELE ──────────────────────────────────────────
  // Az arany-alapu jelvenyek (atlag korty/parti, atlag pont/parti, win rate)
  // vissza tudnak esni egy gyenge parti utan. Ha ezek beleszamitananak az
  // XP-be, a jatekos szintet VESZTENE egy buli utan — ezert kimaradnak.
  console.log('\n===== MONOTONITAS: A SZINT NEM ESHET VISSZA =====');
  p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs3 = []; p.on('pageerror', e => errs3.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed(0));
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  const mono = await p.evaluate(() => {
    // 180 korty / 9 parti = 20 atlag → mind a harom avgd-fokozat megvan.
    // Egy 9 kortyos parti utan: 189/10 = 18.9 → a 20-as fokozat "elveszne".
    const before = { totalPoints:60, totalRounds:200, totalSessions:9, totalWins:1, totalDrinks:180 };
    const after  = { totalPoints:63, totalRounds:212, totalSessions:10, totalWins:1, totalDrinks:189 };
    const xb = window.computeXp(before).total, xa = window.computeXp(after).total;
    return { xb, xa, lb: window.levelFromXp(xb).level, la: window.levelFromXp(xa).level,
             // a jelveny-vitrinben viszont TOVABBRA is latszania kell a valtozasnak
             ratioStillTracked: window.ACHIEVEMENTS.some(a => a.ratio) };
  });
  ok('a parti utan az XP NEM csokkent', mono.xa >= mono.xb, JSON.stringify(mono));
  // 42 (3 pont·10 + 12 kor·1) + 100 (a 10. parti = „Tizes" jelveny, 2. fokozat).
  // A javitas ELOTT ebbol levonodott volna 150 (az elveszett avgd-fokozat),
  // vagyis a jatekos −8 XP-vel zarta volna a bulit.
  ok('a novekmeny pozitiv es pontos: +142 (42 parti + 100 „Tízes" jelvény)', mono.xa - mono.xb === 142, `${mono.xb} → ${mono.xa}`);
  ok('a szint sem esett vissza', mono.la >= mono.lb, `${mono.lb}. → ${mono.la}.`);
  ok('az arany-alapu jelvenyek megmaradtak a vitrinben', mono.ratioStillTracked === true);
  ok('nincs JS hiba', errs3.filter(e => !/ServiceWorker/.test(e)).length === 0, errs3.join(' | '));
  await p.close();

  // ── Profil nelkuli jatekosok: ne omoljon ossze ─────────────────────────
  console.log('\n===== PROFIL NELKULI JATEKOSOK =====');
  p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs2 = []; p.on('pageerror', e => errs2.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed(0));
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  await p.evaluate(`
    const root = document.createElement('div'); root.id='__es';
    root.style.cssText='position:fixed;inset:0;background:#F5D89B;overflow:auto;z-index:1';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(window.EndScreen, {
      players: [ { id:'a', name:'Anna', color:'#5BA0DB', points:5, drinks:2 },
                 { id:'b', name:'Bela', color:'#E07A5F', points:1, drinks:3 } ],
      go: ()=>{}, resetGame: ()=>{}, lastRound: 4, scoreHistory: null,
    }));
  `);
  await p.waitForTimeout(1600);
  const t3 = await p.evaluate(() => document.getElementById('__es').innerText);
  ok('a végeredmény kirajzolódik', /Anna/.test(t3) && /Bela/.test(t3));
  ok('XP-kártya NINCS (nincs mihez kötni)', !/SZINTEK — A MAI ESTÉBŐL/i.test(t3));
  ok('nincs JS hiba', errs2.filter(e => !/ServiceWorker/.test(e)).length === 0, errs2.join(' | '));
  await p.close();

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
