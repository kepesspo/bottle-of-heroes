// v10.376 — Beer Pong 2.0: izolált duplikátum
//
// A Beer Pong 2.0 a Beer Pong Torna külön komponens-stackje (BeerPong2*), saját
// config-kulccsal (beerpong2Config) és szoba-mezővel (bp2State). A cél: a
// meglévő Beer Pong ÉRINTETLEN maradjon, miközben a 2.0-ra épülnek az új
// funkciók.
//
// Fogódzók:
//  1) a 2.0 játék végigjátszható és bajnokot hirdet, a bajnok pontot kap (onAdvance)
//  2) IZOLÁCIÓ: a 2.0 a szobába `bp2State`-et ír, `bpState`-et NEM
//  3) IZOLÁCIÓ visszafelé: a régi Beer Pong `bpState`-et ír, `bp2State`-et NEM
//  4) a 2.0 observer a `bp2State`-ből rajzol (nem üres)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

async function open(b) {
  const p = await b.newPage({ viewport: { width: 402, height: 1000 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

// Mount tetszőleges BP-komponenst (BeerPongGame vagy BeerPong2Game), adott config-kulccsal.
const mountBp = (p, compName, metaKey, names, cfg, roomCode) => p.evaluate(({ compName, metaKey, names, cfg, roomCode }) => {
  const cols = ['#E07A5F','#4FC2A0','#A78BFA','#5BA0DB'];
  const pl = names.map((n, i) => ({ id: 'p' + i, name: n, color: cols[i % cols.length], points:0, drinks:0 }));
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  let root = document.getElementById('__p'); if (root) root.remove();
  root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto';
  document.body.appendChild(root);
  window.__adv = null;
  window.__cupRows = () => [...document.querySelectorAll('#__p div')].filter(d => {
    const k = [...d.children];
    return k.length === 3 && k[0].tagName === 'BUTTON' && k[2].tagName === 'BUTTON'
      && (k[0].textContent || '').trim() === '−' && (k[2].textContent || '').trim() === '+';
  });
  const Comp = window[compName];
  ReactDOM.createRoot(root).render(React.createElement(Comp, {
    gameIdx: 0, players: pl, gameMeta: { [metaKey]: cfg }, roomCode: roomCode || null, initialBpState: null,
    onAdvance: (dm, pm) => { window.__adv = { dm, pm }; }, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
}, { compName, metaKey, names, cfg, roomCode });

const cupCeiling = (p, which) => p.evaluate(async (which) => {
  const row = () => window.__cupRows()[which];
  if (window.__cupRows().length < 2) return null;
  let last = -1;
  for (let i = 0; i < 40; i++) {
    const r = row(); if (!r) break;
    [...r.children][2].click();
    await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
    const v = parseInt(([...row().children][1].textContent || '').trim(), 10);
    if (v === last) break;
    last = v;
  }
  return last;
}, which);
const confirm = p => p.evaluate(() => {
  const x = [...document.querySelectorAll('#__p button')].find(y => /nyert — tovább|Döntetlen megerősítése/.test(y.textContent || ''));
  if (!x || x.disabled) return 'NINCS'; x.click(); return 'ok';
});
const pageTxt = p => p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. A 2.0 végigjátszható, bajnokot hirdet, a bajnok pontot kap ──
  console.log('\n===== 1. BEER PONG 2.0 — VÉGIGJÁTSZHATÓ, BAJNOK =====');
  {
    const p = await open(b);
    await mountBp(p, 'BeerPong2Game', 'beerpong2Config', ['Sere', 'Kecsi'],
      { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:6, visszavago:false, matchMinutes:0 }, null);
    await p.waitForTimeout(1500);
    ok((await cupCeiling(p, 0)) === 6, 'a 2.0 döntőben a finalCups=6 a plafon (a motor működik)', await cupCeiling(p, 0));
    await p.waitForTimeout(150);
    ok(await confirm(p) === 'ok', 'a megerősítés élő');
    await p.waitForTimeout(1200);
    ok(/Bajnok|🏆/.test(await pageTxt(p)), 'a 2.0 bajnokot hirdet', (await pageTxt(p)).slice(0, 80));
    const adv = await p.evaluate(() => window.__adv);
    ok(adv && adv.pm && Object.values(adv.pm).some(v => v > 0), 'a bajnok pontot kap (onAdvance pm)', adv && JSON.stringify(adv.pm));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 2. IZOLÁCIÓ: a 2.0 bp2State-et ír, bpState-et NEM ──
  console.log('\n===== 2. IZOLÁCIÓ — a 2.0 bp2State-et ír =====');
  {
    const p = await open(b);
    await mountBp(p, 'BeerPong2Game', 'beerpong2Config', ['Sere', 'Kecsi', 'Vivi', 'Robi'],
      { tournamentType:'se', mode:'egyeni', maxCups:10, matchMinutes:0 }, '770055');
    await p.waitForTimeout(1500);
    const room = await p.evaluate(() => window.__fbStore['rooms']['770055'] || {});
    ok(!!room.bp2State, '⚠️ a 2.0 a szobába `bp2State`-et ír', !!room.bp2State);
    ok(!room.bpState, '⚠️ és `bpState`-et NEM (nem szennyezi a régi mezőt)', room.bpState === undefined ? 'nincs bpState' : 'VAN bpState!');
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 3. IZOLÁCIÓ visszafelé: a RÉGI Beer Pong bpState-et ír, bp2State-et NEM ──
  console.log('\n===== 3. IZOLÁCIÓ — a régi Beer Pong bpState-et ír (érintetlen) =====');
  {
    const p = await open(b);
    await mountBp(p, 'BeerPongGame', 'beerpongConfig', ['Sere', 'Kecsi', 'Vivi', 'Robi'],
      { tournamentType:'se', mode:'egyeni', maxCups:10, matchMinutes:0 }, '770066');
    await p.waitForTimeout(1500);
    const room = await p.evaluate(() => window.__fbStore['rooms']['770066'] || {});
    ok(!!room.bpState, 'a régi Beer Pong `bpState`-et ír (változatlan)', !!room.bpState);
    ok(!room.bp2State, 'és `bp2State`-et NEM', room.bp2State === undefined ? 'nincs bp2State' : 'VAN bp2State!');
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 4. A 2.0 observer a bp2State-ből rajzol ──
  console.log('\n===== 4. A 2.0 OBSERVER — bp2State-ből rajzol =====');
  {
    const p = await open(b);
    const txt = await p.evaluate(() => {
      const code = '770077';
      window.__fbStore['rooms'] = { [code]: {
        code, players: [{ id:'p0', name:'Sere', color:'#E07A5F' }, { id:'p1', name:'Kecsi', color:'#4FC2A0' }],
        gameIdx: 0, selectedGames: ['beerpong2'],
        bp2State: { tournament:'se', phase:'groups',
          seRounds: { '0': [{ p1:{id:'p0',name:'Sere',color:'#E07A5F'}, p2:{id:'p1',name:'Kecsi',color:'#4FC2A0'}, winner:null, loser:null, score:null }] },
          seCurRound:0, seCurMatch:0, cups1:0, cups2:0, rrMatches:[], tsGroups:[], champion:null, drinkMap:{} },
      } };
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const root = document.createElement('div'); root.id = '__o';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto;background:#fff';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(BeerPong2ObserverView, {
        room: window.__fbStore['rooms'][code], code, onLeave: () => {} }));
      return null;
    });
    await p.waitForTimeout(600);
    const otxt = await p.evaluate(() => (document.getElementById('__o').innerText || '').replace(/\s+/g, ' '));
    ok(/Sere/.test(otxt) && /Kecsi/.test(otxt), 'a 2.0 observer a meccset mutatja a bp2State-ből', otxt.slice(0, 80));
    ok(/Beer Pong/i.test(otxt), 'és a Beer Pong fejléc kint van', /Beer Pong/i.test(otxt));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
