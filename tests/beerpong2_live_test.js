// v10.386 — Beer Pong 2.0: NINCS asztal-limit + per-meccs óra (bp2Live)
//
// A bejelentett probléma: az observeren nem lehetett meccset KIVÁLASZTANI, és
// nem lehetett 2 külön meccset kezelni (a `tables` cap döntött helyettünk).
// Innentől a kör MINDEN függő meccse egy kártya, bármelyik INDÍTHATÓ (per-meccs
// óra) és BEKÜLDHETŐ — asztal-limit nélkül. A host validál, de indíthat is.
//
// Fogódzók (4 játékos, 2 elődöntő, matchMinutes:5, tables:1 a configban):
//  1) a telefon MINDKÉT függő meccset mutatja (a tables:1 cap MEGSZŰNT)
//  2) minden kártyán van „Indítás" (matchMinutes>0), óra még nincs
//  3) az egyik meccs indítása → bp2Live 1 kulcs, óra (mm:ss) jelenik meg,
//     a MÁSIK kártyán még „Indítás" áll (független meccsek)
//  4) a host „Élő meccsek" panelje mutatja mindkettőt, az egyiken órával
//  5) beküldés + host elfogadás → a bp2Live törlődik arra a meccsre
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990386';
const live = p => p.evaluate(c => (window.__fbStore['rooms'][c] || {}).bp2Live || {}, CODE);
const phoneCards = p => p.evaluate(() => [...document.querySelectorAll('#__phone button')].filter(b => /Beküldés a hostnak|Állítsd be az eredményt/.test(b.textContent || '')).length);
const phoneStartBtns = p => p.evaluate(() => [...document.querySelectorAll('#__phone button')].filter(b => /Indítás/.test(b.textContent || '')).length);
const phoneTxt = p => p.evaluate(() => (document.getElementById('__phone').innerText || '').replace(/\s+/g, ' '));
const hostTxt = p => p.evaluate(() => (document.getElementById('__host').innerText || '').replace(/\s+/g, ' '));

const roundMatches = p => p.evaluate(c => {
  const bp = window.__fbStore['rooms'][c].bp2State;
  const rObj = bp.seRounds; const r0 = Array.isArray(rObj) ? rObj[bp.seCurRound ?? 0] : Object.values(rObj)[bp.seCurRound ?? 0];
  const arr = Array.isArray(r0) ? r0 : Object.values(r0);
  return arr.filter(m => m && m.p1 && m.p2 && m.winner == null).map(m => ({ p1id: m.p1.id, p2id: m.p2.id, p1name: m.p1.name, p2name: m.p2.name }));
}, CODE);

const submitOne = (p, s) => p.evaluate(({ code, s }) => {
  const ref = firebase.firestore().collection('rooms').doc(code);
  return ref.set({ bp2Submit: { [s.p1id + '__' + s.p2id]: { p1id: s.p1id, p2id: s.p2id, p1name: s.p1name, p2name: s.p2name, p1: s.p1, p2: s.p2, by: s.by, ts: Date.now() } } }, { merge: true });
}, { code: CODE, s });

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
    window.__adv = null;
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:900px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      // tables:1 SZÁNDÉKOSAN — a régi cap 1 kártyát mutatott volna; most 2-t kell
      gameMeta: { beerpong2Config: { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:5, tables:1, thirdPlace:false } },
      onAdvance: (dm, pm) => { window.__adv = { dm, pm }; }, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
    const f = document.createElement('div'); f.id = '__phone';
    f.style.cssText = 'position:absolute;left:0;top:920px;width:402px;height:760px;overflow:auto;z-index:9;background:#fff';
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

  // ── 1. NINCS cap: mindkét elődöntő látszik a telefonon ──
  console.log('\n===== 1. NINCS ASZTAL-LIMIT — 2 kártya (tables:1 ellenére) =====');
  const semis = await roundMatches(p);
  ok(semis.length === 2, 'a 0. kör 2 elődöntő', semis.length);
  ok(await phoneCards(p) === 2, '⚠️ a telefon MINDKÉT meccset mutatja (a tables:1 cap megszűnt)', await phoneCards(p));

  // ── 2. Minden kártyán „Indítás" (matchMinutes>0), óra még nincs ──
  console.log('\n===== 2. INDÍTÁS gombok, óra még nincs =====');
  ok(await phoneStartBtns(p) === 2, 'mindkét kártyán van „Indítás" gomb', await phoneStartBtns(p));
  ok(Object.keys(await live(p)).length === 0, 'még egy meccs sincs elindítva (bp2Live üres)');

  // ── 3. Az egyik meccs indítása → óra jelenik meg, a másik érintetlen ──
  console.log('\n===== 3. EGY MECCS INDÍTÁSA → per-meccs óra =====');
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__phone button')].find(x => /Indítás/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(500);
  const lv = await live(p);
  ok(Object.keys(lv).length === 1, 'bp2Live pontosan 1 elindított meccset tartalmaz', Object.keys(lv).length);
  ok(/\d\d:\d\d/.test(await phoneTxt(p)), 'megjelent a visszaszámláló (mm:ss) a telefonon', (await phoneTxt(p)).match(/\d\d:\d\d/));
  ok(await phoneStartBtns(p) === 1, 'a MÁSIK meccsen még „Indítás" áll (független meccsek)', await phoneStartBtns(p));

  // ── 4. Nincs külön „Élő meccsek" panel a hoston (beolvadt a párosításokba — v10.387) ──
  console.log('\n===== 4. NINCS KÜLÖN „ÉLŐ MECCSEK" PANEL =====');
  ok(!/Élő meccsek/i.test(await hostTxt(p)), '⚠️ a hoston NINCS külön „Élő meccsek" blokk (a párosításokba került)', (await hostTxt(p)).match(/Élő meccsek/));

  // ── 5. Beküldés + host elfogadás → bp2Live törlődik arra a meccsre ──
  console.log('\n===== 5. ELFOGADÁS TÖRLI A PER-MECCS ÓRÁT =====');
  const startedKey = Object.keys(lv)[0];
  const started = semis.find(s => (s.p1id + '__' + s.p2id) === startedKey) || semis[0];
  await submitOne(p, { ...started, p1:10, p2:6, by:'asztal' });
  await p.waitForTimeout(600);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__host button')].find(x => /Elfogadom és rögzítem/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(900);
  ok(!((await live(p))[startedKey]), '⚠️ az elfogadott meccs bp2Live-bejegyzése törlődött', JSON.stringify(await live(p)));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
