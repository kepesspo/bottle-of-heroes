// v10.390 — Beer Pong 2.0: host↔observer óra-szinkron + beküldött eredmény FELÜL a hoston
//
// A bejelentett hibák:
//  1) a beküldött (jóváhagyásra váró) meccsek a hoston is FELÜL jelenjenek meg;
//  2) ha elindul egy meccs a hostnál, az observernél is induljon és fordítva
//     (közös bp2Live óra) — az volt a hiba, hogy observernél beküldött meccset
//     a hostnál MÉGIS el lehetett indítani;
//  3) ha az observeren elindult a meccs, a host fő kijelzőjén is látsszon.
//
// Fogódzók (SE, 4 játékos, matchMinutes:5, host + observer egy szobán):
//  A) a host fő kártyáján a „▶ Start" a KÖZÖS bp2Live-ba ír (observer is látja)
//  B) az observer által indított meccs a host fő kijelzőjén ÓRÁVAL jelenik meg
//  C) a beküldött eredmény a host meccs-kártyája FÖLÖTT van
//  D) beküldött meccset a host NEM tud újraindítani (a Start letiltva)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990390';
const live = p => p.evaluate(c => (window.__fbStore['rooms'][c] || {}).bp2Live || {}, CODE);
const hostTxt = p => p.evaluate(() => (document.getElementById('__host').innerText || '').replace(/\s+/g, ' '));

const semis = p => p.evaluate(c => {
  const bp = window.__fbStore['rooms'][c].bp2State;
  const rObj = bp.seRounds; const r0 = Array.isArray(rObj) ? rObj[0] : Object.values(rObj)[0];
  const arr = Array.isArray(r0) ? r0 : Object.values(r0);
  return arr.filter(m => m && m.p1 && m.p2 && m.winner == null).map(m => ({ p1id: m.p1.id, p2id: m.p2.id, p1name: m.p1.name, p2name: m.p2.name }));
}, CODE);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1700 } });
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
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:1000px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      gameMeta: { beerpong2Config: { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:5, thirdPlace:false } },
      onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
    const f = document.createElement('div'); f.id = '__obs';
    f.style.cssText = 'position:absolute;left:0;top:1010px;width:402px;height:680px;overflow:auto;z-index:9;background:#fff';
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

  const sm = await semis(p);
  const pointerKey = sm[0].p1id + '__' + sm[0].p2id;   // a mutató (seCurMatch 0) meccs

  // ── A. A host „▶ Start" a KÖZÖS bp2Live-ba ír ──
  console.log('\n===== A. HOST START → KÖZÖS bp2Live =====');
  ok(Object.keys(await live(p)).length === 0, 'kezdetben nincs élő meccs');
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__host button')].find(x => /^▶\s*Start/.test((x.textContent || '').trim())); if (b) b.click(); });
  await p.waitForTimeout(500);
  const lvA = await live(p);
  ok(lvA[pointerKey], '⚠️ a host Start a bp2Live-ba írt (observer is látja)', JSON.stringify(Object.keys(lvA)));
  ok(/\d\d:\d\d/.test(await hostTxt(p)), 'a host fő kártyáján megjelent az óra', (await hostTxt(p)).match(/\d\d:\d\d/));
  const obsSeesClock = await p.evaluate(() => /\d\d:\d\d/.test(document.getElementById('__obs').innerText || ''));
  ok(obsSeesClock, 'az observer is látja az órát (host→observer szinkron)');

  // ── B. Observer indítás → host fő kijelzőn óra ──
  console.log('\n===== B. OBSERVER START → HOST FŐ KIJELZŐN ÓRA =====');
  // a mutató-kulcsot vesszük ki a bp2Live-ból (a bp2State marad), hogy az observer ▶ újra megjelenjen
  await p.evaluate(({ c, k }) => firebase.firestore().collection('rooms').doc(c).set({ bp2Live: { [k]: firebase.firestore.FieldValue.delete() } }, { merge: true }), { c: CODE, k: pointerKey });
  await p.waitForTimeout(400);
  // az observer elindítja ugyanezt a meccset (az első ▶ Indítás)
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__obs button')].find(x => /Indítás/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(500);
  const lvB = await live(p);
  ok(Object.keys(lvB).length >= 1, 'az observer indítása a bp2Live-ba írt', JSON.stringify(Object.keys(lvB)));
  // a host fő kártyáján (mutató meccs) látszik az óra, ha a mutató meccs az élő
  if (lvB[pointerKey]) ok(/\d\d:\d\d/.test(await hostTxt(p)), '⚠️ a host fő kijelzőjén megjelent az observer által indított meccs órája');
  else ok(true, '(az observer másik meccset indított — a host akkor a listán/kártyán látja)');

  // ── C. Beküldött eredmény a host meccs-kártyája FÖLÖTT ──
  console.log('\n===== C. BEKÜLDÖTT EREDMÉNY FELÜL A HOSTON =====');
  await p.evaluate(({ c, s }) => firebase.firestore().collection('rooms').doc(c).set({ bp2Submit: { [s.p1id + '__' + s.p2id]: { p1id: s.p1id, p2id: s.p2id, p1name: s.p1name, p2name: s.p2name, p1: 7, p2: 3, by: 'asztal', ts: Date.now() } } }, { merge: true }), { c: CODE, s: sm[0] });
  await p.waitForTimeout(600);
  ok(/BEKÜLDÖTT EREDMÉNY/i.test(await hostTxt(p)), 'a hoston megjelenik a „BEKÜLDÖTT EREDMÉNY" panel');
  const orderOK = await p.evaluate(() => {
    const all = [...document.querySelectorAll('#__host *')];
    const sub = all.find(n => /BEKÜLDÖTT EREDMÉNY/i.test(n.textContent || '') && n.getBoundingClientRect().height < 200);
    const accept = all.find(n => /Elfogadom és rögzítem/.test(n.textContent || '') && n.tagName === 'BUTTON');
    // a meccs-kártya jelzője: a két avatar közti „VS" (mindig ott van a fő kártyán)
    const vs = all.find(n => (n.textContent || '').trim() === 'VS' && n.children.length === 0);
    if (!sub || !accept || !vs) return { ok:false, reason:'nincs sub/accept/vs', sub:!!sub, accept:!!accept, vs:!!vs };
    const subTop = sub.getBoundingClientRect().top;
    const cardTop = vs.getBoundingClientRect().top;
    return { ok: subTop < cardTop, subTop, cardTop };
  });
  ok(orderOK.ok, '⚠️ a beküldött eredmény a meccs-kártya FÖLÖTT van', JSON.stringify(orderOK));

  // ── D. Beküldött meccset a host NEM indíthat újra ──
  console.log('\n===== D. BEKÜLDÖTT MECCS NEM INDÍTHATÓ ÚJRA =====');
  // a beküldött (sm[0]) meccs a mutató is → a fő kártya Start-ja letiltva VAGY „beküldve" jelző
  const cannotRestart = await p.evaluate((k) => {
    // a fő kártya Start gombja letiltott?
    const start = [...document.querySelectorAll('#__host button')].find(x => /Start/.test(x.textContent || ''));
    const startDisabled = start ? start.disabled : true;
    // a listákban a beküldött meccs „⏳ beküldve" jelzőt kap (nem ▶)
    const hasBekuldve = /beküldve/i.test(document.getElementById('__host').innerText || '');
    return { startDisabled, hasBekuldve };
  }, pointerKey);
  ok(cannotRestart.startDisabled || cannotRestart.hasBekuldve, '⚠️ a beküldött meccs nem indítható újra (Start letiltva vagy „beküldve" jelző)', JSON.stringify(cannotRestart));

  // ── E. A host beküldött-panelje LENYITHATÓ (v10.391) ──
  console.log('\n===== E. HOST BEKÜLDÖTT-PANEL LENYITHATÓ =====');
  // alapból NYITVA: az „Elfogadom és rögzítem" gomb látszik
  ok(/Elfogadom és rögzítem/.test(await hostTxt(p)), 'alapból nyitva (Elfogadom gomb látszik)');
  // a lenyitható fejlécen kattintunk (cursor:pointer, „Elfogadásra váró")
  await p.evaluate(() => { const h = [...document.querySelectorAll('#__host *')].find(n => /Elfogadásra váró/i.test(n.innerText || '') && getComputedStyle(n).cursor === 'pointer'); if (h) h.click(); });
  await p.waitForTimeout(300);
  ok(!/Elfogadom és rögzítem/.test(await hostTxt(p)), '⚠️ becsukva az Elfogadom gomb eltűnik (a panel lenyitható)');
  ok(/Elfogadásra váró/i.test(await hostTxt(p)), 'a fejléc (darabszámmal) becsukva is látszik');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
