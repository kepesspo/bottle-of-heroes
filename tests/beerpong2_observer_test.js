// v10.389 — Beer Pong 2.0 observer: beküldött eredmény FELÜL + lenyitható,
// beküldéskor leáll az időzítő, nagy kijelzőn kompakt rács.
//
// Fogódzók (SE, 4 játékos, matchMinutes:5, nagy kijelző):
//  1) a nyitott meccsek RÁCSBAN vannak (nagy kijelzőn nem egy oszlop) — #3
//  2) egy meccs indítása → óra; beküldés után az óra LEÁLL (bp2Live törlődik) — #2
//  3) a beküldött eredmény FELÜL, lenyitható panelben („host jóváhagyására vár (N)"),
//     alapból zárva; lenyitva látszik az eredmény-sor — #1
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990389';
const live = p => p.evaluate(c => (window.__fbStore['rooms'][c] || {}).bp2Live || {}, CODE);
const phoneTxt = p => p.evaluate(() => (document.getElementById('__phone').innerText || '').replace(/\s+/g, ' '));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1300, height: 1000 } });   // NAGY kijelző
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ code }) => {
    const pl = [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
                { id:'p2', name:'Vivi', color:'#A78BFA', points:0, drinks:0 },
                { id:'p3', name:'Robi', color:'#5BA0DB', points:0, drinks:0 }];
    window.__fbStore['rooms'] = { [code]: { code, players: pl, gameIdx: 0, selectedGames: ['beerpong2'] } };
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    // host (a bp2State-hez), rejtve
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:-3000px;top:0;width:402px;height:900px;overflow:auto';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      gameMeta: { beerpong2Config: { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:5, thirdPlace:false } },
      onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
    // observer — SZÉLES konténer, hogy a rács kihasználható legyen
    const f = document.createElement('div'); f.id = '__phone';
    f.style.cssText = 'position:absolute;left:0;top:0;width:1240px;height:1000px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(f);
    function W() {
      const [room, setRoom] = React.useState(() => window.__fbStore['rooms'][code]);
      React.useEffect(() => firebase.firestore().collection('rooms').doc(code).onSnapshot(s => setRoom(s.data() || null)), []);
      if (!room) return null;
      return React.createElement(BeerPong2ObserverView, { room, code, observerName: 'Néző', onLeave: () => {} });
    }
    ReactDOM.createRoot(f).render(React.createElement(W));
  }, { code: CODE });
  await p.waitForTimeout(1800);

  // ── 1. Nagy kijelzőn a nyitott meccsek RÁCSBAN ──
  console.log('\n===== 1. NAGY KIJELZŐ — KOMPAKT RÁCS =====');
  const gridOK = await p.evaluate(() => {
    const cards = [...document.querySelectorAll('#__phone *')].filter(n => /Állítsd be az eredményt|Beküldés a hostnak/.test(n.textContent || ''));
    // a meccs-kártyák közös szülője rács-e (display:grid, több oszlop)
    const grid = [...document.querySelectorAll('#__phone div')].find(d => getComputedStyle(d).display === 'grid' && /minmax/.test(d.style.gridTemplateColumns || ''));
    if (!grid) return { grid:false };
    const cols = getComputedStyle(grid).gridTemplateColumns.split(' ').length;
    return { grid:true, cols };
  });
  ok(gridOK.grid, 'a nyitott meccsek RÁCS-konténerben vannak (display:grid, minmax)', JSON.stringify(gridOK));
  ok(gridOK.cols >= 2, '⚠️ nagy kijelzőn a rács TÖBB oszlopos (nem foglal el egy egész oszlopot)', gridOK.cols);

  // ── 2. Indítás → óra; beküldés után az óra LEÁLL ──
  console.log('\n===== 2. BEKÜLDÉSKOR LEÁLL AZ IDŐZÍTŐ =====');
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__phone button')].find(x => /Indítás/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(400);
  ok(Object.keys(await live(p)).length === 1, 'az első meccs elindult (bp2Live 1 kulcs)', Object.keys(await live(p)).length);
  ok(/\d\d:\d\d/.test(await phoneTxt(p)), 'megjelent az óra', (await phoneTxt(p)).match(/\d\d:\d\d/));
  // az elindított meccs (első kártya) p1-jére +1, majd beküldés
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__phone button')].find(x => (x.textContent || '').trim() === '+'); if (b) b.click(); });
  await p.waitForTimeout(200);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__phone button')].find(x => /Beküldés a hostnak/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(500);
  ok(Object.keys(await live(p)).length === 0, '⚠️ beküldés után az időzítő LEÁLLT (bp2Live törlődött)', JSON.stringify(await live(p)));

  // ── 3. A beküldött eredmény FELÜL, lenyitható, alapból zárva ──
  console.log('\n===== 3. BEKÜLDÖTT EREDMÉNY FELÜL, LENYITHATÓ =====');
  const t3 = await phoneTxt(p);
  ok(/host jóváhagyására vár/i.test(t3), 'a beküldött-panel fejléce látszik („host jóváhagyására vár")');
  // alapból ZÁRVA: a fejléc-szám (1) látszik, de a nevekkel az eredmény-sor NEM
  const collapsed = await p.evaluate(() => {
    const hdr = [...document.querySelectorAll('#__phone *')].find(n => /host jóváhagyására vár/i.test((n.innerText || '')) && (n.innerText || '').length < 80);
    return hdr ? hdr.innerText.replace(/\s+/g, ' ') : '';
  });
  ok(/\b1\b/.test(collapsed), 'a fejléc a beküldött meccsek SZÁMÁT mutatja (1)', collapsed);
  // felül van-e? a panel a rács ELŐTT jön a DOM-ban
  const orderOK = await p.evaluate(() => {
    const txt = document.getElementById('__phone').innerText || '';
    const iPanel = txt.search(/host jóváhagyására vár/i);
    const iGrid = txt.search(/Állítsd be az eredményt|Beküldés a hostnak/);
    return iGrid === -1 ? true : (iPanel >= 0 && iPanel < iGrid);
  });
  ok(orderOK, '⚠️ a beküldött eredmény FELÜL van (a játszható meccsek előtt)');
  // lenyitás után látszik az eredmény-sor
  await p.evaluate(() => { const h = [...document.querySelectorAll('#__phone *')].find(n => /host jóváhagyására vár/i.test((n.innerText || '')) && n.getBoundingClientRect().height < 80); if (h) h.click(); });
  await p.waitForTimeout(300);
  ok(/–/.test(await phoneTxt(p)), 'lenyitva látszik a beküldött eredmény (pontszám-sor)');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
