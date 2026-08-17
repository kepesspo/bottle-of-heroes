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
const hostTxt = p => p.evaluate(() => (document.getElementById('__host') ? (document.getElementById('__host').innerText || '') : '').replace(/\s+/g, ' '));

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

  // ── 0. Nagy kijelzős layout: nincs „Aktuális meccs", eredmény a jobb oszlopban, standings a meccsek felett (v10.392) ──
  console.log('\n===== 0. NAGY KIJELZŐS LAYOUT (v10.392) =====');
  ok(!/Aktuális meccs/i.test(await phoneTxt(p)), '⚠️ NINCS „Aktuális meccs" kártya az observeren');
  // egy lezárt meccset ültetünk a bp2State-be, hogy az „Eredmények" panel megjelenjen
  await p.evaluate(c => {
    const bp = window.__fbStore['rooms'][c].bp2State;
    const r = Array.isArray(bp.seRounds) ? bp.seRounds : Object.values(bp.seRounds);
    const m = (Array.isArray(r[0]) ? r[0] : Object.values(r[0]))[0];
    m.score = { p1: 10, p2: 5 }; m.winner = m.p1; m.loser = m.p2;
    firebase.firestore().collection('rooms').doc(c).set({ __ping: Date.now() }, { merge: true });
  }, CODE);
  await p.waitForTimeout(500);
  const layout = await p.evaluate(() => {
    // a levél-elemeket keressük (pontos felirat), nem a teljes-szélességű ősüket
    const results = [...document.querySelectorAll('#__phone *')].find(n => /^📋\s*Eredmények$/i.test((n.textContent||'').trim()) && n.children.length === 0);
    const grid = [...document.querySelectorAll('#__phone div')].find(d => getComputedStyle(d).display === 'grid' && /minmax/.test(d.style.gridTemplateColumns || ''));
    const stand = [...document.querySelectorAll('#__phone *')].find(n => /^🏆\s*Kieséses ágrajz$/i.test((n.textContent||'').trim()) && n.children.length === 0);
    if (!grid) return { ok:false };
    const gr = grid.getBoundingClientRect();
    const rr = results ? results.getBoundingClientRect() : null;
    const sr = stand ? stand.getBoundingClientRect() : null;
    return {
      hasResults: !!results,
      resultsRight: rr ? rr.left > gr.right - 40 : null,   // az Eredmények a rács jobbján (jobb oszlop)
      standAboveMatches: sr ? sr.top < gr.top : null,      // a standings a meccs-rács FÖLÖTT
    };
  });
  ok(layout.hasResults, 'az „Eredmények" panel megvan');
  ok(layout.resultsRight === true, '⚠️ az „Eredmények" a JOBB oszlopban van (a meccs-rács jobbján)', JSON.stringify(layout));
  ok(layout.standAboveMatches === true, '⚠️ nagy kijelzőn a standings a meccsek FÖLÖTT van', JSON.stringify(layout));

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
  // lenyitás: a lenyitható fejlécen (cursor:pointer) kattintunk — a külső panel-div nem kattintható
  await p.evaluate(() => { const h = [...document.querySelectorAll('#__phone *')].find(n => /host jóváhagyására vár/i.test((n.innerText || '')) && getComputedStyle(n).cursor === 'pointer'); if (h) h.click(); });
  await p.waitForTimeout(300);
  ok(/Módosítás/.test(await phoneTxt(p)), 'lenyitva látszik a beküldött sor a „✏️ Módosítás" gombbal');

  // ── 4. A beküldött eredmény MÓDOSÍTHATÓ → a store (és így a host) frissül (v10.391) ──
  console.log('\n===== 4. BEKÜLDÖTT EREDMÉNY MÓDOSÍTÁSA =====');
  const subKey = await p.evaluate(c => Object.keys((window.__fbStore['rooms'][c] || {}).bp2Submit || {})[0], CODE);
  const before = await p.evaluate(({ c, k }) => (window.__fbStore['rooms'][c].bp2Submit[k]), { c: CODE, k: subKey });
  ok(!!subKey, 'van beküldött meccs a store-ban', subKey);
  // „✏️ Módosítás" → a meccs visszakerül a szerkeszthető (nyitott) közé
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__phone button')].find(x => /Módosítás/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(300);
  ok(/Módosítás beküldése/.test(await phoneTxt(p)), 'a szerkesztő kártya „Módosítás beküldése" gombot mutat (előtöltve)');
  // a szerkesztő kártyán a p2 „+"-t kétszer nyomjuk (más eredmény), majd újra beküldjük
  const changed = await p.evaluate(() => {
    const card = [...document.querySelectorAll('#__phone div')].find(d => /Módosítás —/.test(d.textContent || '') && d.querySelectorAll('button').length >= 5 && d.querySelectorAll('button').length < 9);
    if (!card) return false;
    const plus = [...card.querySelectorAll('button')].filter(x => x.textContent.trim() === '+');
    if (plus[1]) { plus[1].click(); plus[1].click(); }   // p2 +2
    return true;
  });
  ok(changed, 'megtalált a szerkesztő kártya');
  await p.waitForTimeout(200);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__phone button')].find(x => /Módosítás beküldése/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(500);
  const after = await p.evaluate(({ c, k }) => (window.__fbStore['rooms'][c].bp2Submit[k]), { c: CODE, k: subKey });
  ok(after && (after.p1 !== before.p1 || after.p2 !== before.p2), '⚠️ a beküldött eredmény a store-ban MEGVÁLTOZOTT (a host is ezt olvassa)', JSON.stringify(before) + ' → ' + JSON.stringify(after));
  // a host (rejtett) is az új eredményt látja
  ok((await hostTxt(p)).includes(after.p1 + ' – ' + after.p2), 'a host jóváhagyó kártyája az ÚJ eredményt mutatja', after.p1 + ' – ' + after.p2);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
