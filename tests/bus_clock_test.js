// v10.330 — Busz: mióta megy a busz (a BohTimer `pill` variánsa, felfelé számol)
//
// A kezdés időbélyege (`busStartedAt`) a SZOBÁBAN ül, nem eszközönként —
// különben minden telefon mást számolna, és a később csatlakozó 0-ról indulna.
// A ketyegés viszont helyi (1 mp-es interval), hogy ne terheljük a Firestore-t
// másodpercenként.
//
// Amit ellenőriz:
//   1. a `startBus` tényleg kiírja a `busStartedAt`-et a szobába;
//   2. az óra a busz fázisban ott van a HOST tábláján, a NÉZŐMÓDBAN és a
//      JÁTÉKOS nézetében is;
//   3. a piramis (első fél) fázisban NINCS ott — ez csak a második félhez kell;
//   4. tényleg ketyeg, és `m:ss` alakban ír.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'p0', name:'Sere', color:'#E0655F' }, { id:'p1', name:'Luca', color:'#A78BFA' },
            { id:'p2', name:'Dani', color:'#4FC2A0' }];
const CARD = (v, s, r) => ({ id:v+s+r, value:v, suit:s, rowIdx:r, faceUp:true });
const ROUTE = [{suit:'♥',value:'2'},{suit:'♦',value:'7'},{suit:'♣',value:'9'},
               {suit:'♠',value:'K'},{suit:'♥',value:'4'},{suit:'♦',value:'3'}];

async function open(b) {
  const p = await b.newPage({ viewport: { width: 402, height: 920 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}
const clocks = p => p.evaluate(() => [...document.querySelectorAll('#__p [role="timer"]')]
  .map(x => ({ aria: x.getAttribute('aria-label') || '', txt: (x.innerText || '').trim(),
               h: Math.round(x.getBoundingClientRect().height) })));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. a felirat formatuma (fuggveny-szinten) ──
  console.log('\n===== 1. A FELIRAT =====');
  let p = await open(b);
  const lbl = await p.evaluate(() => [0, 7, 59, 60, 227, 3600].map(x => bohTimerElapsedLabel(x)));
  ok(lbl.join(',') === '0:00,0:07,0:59,1:00,3:47,60:00', 'm:ss alak, kétjegyű másodperccel', lbl.join(','));

  // ── 2. az ora a BUSZ fazisban ott van, a PIRAMISBAN nincs ──
  console.log('\n===== 2. HOL LATSZIK =====');
  const mountPlayer = (phase) => p.evaluate(({ pl, phase, route }) => {
    const C = (v, s, r) => ({ id:v+s+r, value:v, suit:s, rowIdx:r, faceUp:true });
    const common = { settings:{ deckCount:1, busSteps:6, pyramidRows:5 }, busStartedAt: Date.now() - 227000 };
    const bs = phase === 'pyramid'
      ? { ...common, phase:'pyramid', pyramid:[C('8','♥',6)], nextFlipIdx:1,
          hands:{ p2:[C('10','♦',0)] }, valueCounts:{ '8':1 }, initialDrinks:{ p0:0, p1:0, p2:0 } }
      : { ...common, phase:'bus', busRiders:['p2'], busRiderDone:{}, busWatchers:{},
          busRiderPositions:{ p2:2 }, busRiderDrawnCards:{ p2:[] }, busRouteCards:route,
          busDrawDeck:[{suit:'♣',value:'5'}], busRevealedPositions:[1,3], currentTurnRiderId:'p2',
          busRiderPendingGuesses:{}, busRiderDrinks:{} };
    const room = { players: pl.map(x => ({ ...x, drinks:0 })), buszState: bs, buszTakenIds:['p2'] };
    window.__fbStore['rooms'] = { '424242': room };
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    let root = document.getElementById('__p'); if (root) root.remove();
    root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(BuszPlayerView, { room, roomCode:'424242',
      forcedPlayerId:'p2', forcedBusIntroShown:true, onBusIntroShown:()=>{}, onSwitchToHost:()=>{} }));
  }, { pl: PL, phase, route: ROUTE });

  await mountPlayer('pyramid');
  await p.waitForTimeout(1500);
  const inPyramid = await clocks(p);
  ok(inPyramid.length === 0, 'a PIRAMIS fázisban NINCS óra (csak a második félhez kell)',
     JSON.stringify(inPyramid.map(x => x.txt)));

  await mountPlayer('bus');
  await p.waitForTimeout(1500);
  const inBusPlayer = await clocks(p);
  ok(inBusPlayer.length === 1, 'a JÁTÉKOS nézetében ott az óra a busz fázisban', inBusPlayer.length);
  ok(inBusPlayer[0] && /^3:4[5-9]$/.test(inBusPlayer[0].txt), 'a szobából jövő időbélyeget mutatja (~3:47)',
     inBusPlayer[0] && inBusPlayer[0].txt);
  ok(inBusPlayer[0] && inBusPlayer[0].h === 30, 'a pirula 30 px magas', inBusPlayer[0] && inBusPlayer[0].h);
  ok(inBusPlayer[0] && /Eltelt idő/.test(inBusPlayer[0].aria), 'aria-label: eltelt idő, nem hátralévő');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));

  // ── 3. ketyeg-e ──
  console.log('\n===== 3. KETYEG =====');
  const t0 = (await clocks(p))[0].txt;
  await p.waitForTimeout(2500);
  const t1 = (await clocks(p))[0].txt;
  const secs = x => { const [m, s2] = x.split(':').map(Number); return m * 60 + s2; };
  ok(secs(t1) - secs(t0) >= 2, 'FELFELÉ számol (2,5 mp alatt legalább 2 mp-et lépett)', t0 + ' → ' + t1);

  // ── 3b. a NEZOMODBAN is ott van ──
  // Az a jatekos latja, aki NEM ul a buszon: nala a „👀 Buszozás nézése" gomb
  // nyitja a csak-olvashato tablat.
  console.log('\n===== 3b. NEZOMOD =====');
  await p.evaluate(({ pl, route }) => {
    const bs = { settings:{ deckCount:1, busSteps:6 }, busStartedAt: Date.now() - 227000,
      phase:'bus', busRiders:['p0'], busRiderDone:{}, busWatchers:{},
      busRiderPositions:{ p0:2 }, busRiderDrawnCards:{ p0:[] }, busRouteCards:route,
      busDrawDeck:[{suit:'♣',value:'5'}], busRevealedPositions:[1,3], currentTurnRiderId:'p0',
      busRiderPendingGuesses:{}, busRiderDrinks:{} };
    const room = { players: pl.map(x => ({ ...x, drinks:0 })), buszState: bs, buszTakenIds:['p2'] };
    window.__fbStore['rooms'] = { '424242': room };
    let root = document.getElementById('__p'); if (root) root.remove();
    root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
    document.body.appendChild(root);
    // p2 NEM buszozik → nala jon a „Buszozás nézése" gomb
    ReactDOM.createRoot(root).render(React.createElement(BuszPlayerView, { room, roomCode:'424242',
      forcedPlayerId:'p2', forcedBusIntroShown:true, onBusIntroShown:()=>{}, onSwitchToHost:()=>{} }));
  }, { pl: PL, route: ROUTE });
  await p.waitForTimeout(1600);
  const opened = await p.evaluate(() => {
    const x = [...document.querySelectorAll('#__p button')].find(y => /Buszozás nézése/.test(y.innerText || ''));
    if (x) { x.click(); return true; }
    return false;
  });
  ok(opened, 'megvan a „Buszozás nézése" gomb a nem-buszozónál');
  await p.waitForTimeout(1200);
  const watch = await clocks(p);
  ok(watch.length === 1, 'a NÉZŐMÓDBAN is ott az óra', watch.length);
  ok(watch[0] && /^3:4[5-9]$/.test(watch[0].txt), 'ugyanaz a szoba-időbélyeg (~3:47)', watch[0] && watch[0].txt);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 4. a startBus kiirja a szobaba, es a HOST tablan is ott van ──
  console.log('\n===== 4. A KEZDES IDOBELYEGE A SZOBABAN =====');
  p = await open(b);
  await p.evaluate((pl) => {
    // piramis vege: mindenkinek elfogyott a lapja → a host inditja a buszt
    window.__fbStore['rooms'] = { '424242': { players: pl.map(x => ({ ...x, drinks:0 })),
      buszTakenIds:['p0','p1','p2'],
      buszState:{ phase:'bus', settings:{ deckCount:1, busSteps:6 },
        busRiders:['p0'], busRiderDone:{}, busWatchers:{},
        busRiderPositions:{ p0:2 }, busRiderDrawnCards:{ p0:[] },
        busStartedAt: Date.now() - 65000,
        busRouteCards:[{suit:'♥',value:'2'},{suit:'♦',value:'7'},{suit:'♣',value:'9'},
                       {suit:'♠',value:'K'},{suit:'♥',value:'4'},{suit:'♦',value:'3'}],
        busDrawDeck:[{suit:'♣',value:'5'}], busRevealedPositions:[1,3],
        currentTurnRiderId:'p0', busRiderPendingGuesses:{}, busRiderDrinks:{} } } };
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(BuszGame, { players: pl, roomCode:'424242', gameIdx:0,
      gameMeta:{ buszConfig:{ deckCount:1, busSteps:6 } }, onAdvance:()=>{}, onSetHideFooter:()=>{}, onSetBuszSwitch:()=>{} }));
  }, PL);
  await p.waitForTimeout(2000);
  await p.evaluate(() => { const x = [...document.querySelectorAll('#__p button')].find(y => /Dani/.test(y.innerText||'')); if (x) x.click(); });
  await p.waitForTimeout(500);
  await p.evaluate(() => { const x = [...document.querySelectorAll('#__p button')].find(y => /Válassz|Mehet|Ez vagyok/.test(y.innerText||'')); if (x) x.click(); });
  await p.waitForTimeout(1600);
  const host = await clocks(p);
  ok(host.length === 1, 'a HOST tábláján is ott az óra', host.length);
  ok(host[0] && /^1:0[5-9]$/.test(host[0].txt), 'a host ugyanazt a szoba-időbélyeget mutatja (~1:05)', host[0] && host[0].txt);

  // a `startBus` valoban ir `busStartedAt`-et — forras-szintu ellenorzes, mert
  // a piramis vegigjatszasa egy egesz partit jelentene
  const src = fs.readFileSync(ROOT + '/app.src.html', 'utf8');
  const startBusBlock = (src.match(/phase:'bus', busRiders:riders[\s\S]{0,700}?\}\);/) || [''])[0];
  ok(/busStartedAt: Date\.now\(\)/.test(startBusBlock),
     'a startBus kiírja a busStartedAt-et a szobába', /busStartedAt/.test(startBusBlock) ? 'megvan' : 'HIÁNYZIK');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
