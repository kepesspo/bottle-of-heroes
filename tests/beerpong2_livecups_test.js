// v10.395 — Beer Pong 2.0: ÉLŐ pohárszám-szinkron host ↔ observer
//
// Bejelentés: „host oldalon elindítok egy meccset, a számláló mindkét helyen fut,
// DE amit a host beír, azt az observer nem látja — és fordítva."
// Javítás: elindított (bp2Live) meccsnél a pohárszám a KÖZÖS bp2Live.c1/c2-ból megy.
//
// Fogódzó (2 fő, SE = 1 döntő, matchMinutes:5): a host beírt pohara megjelenik a
// bp2Live-ban (observer olvassa), és az observer beírt pohara a hoston.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990395';
const KEY = 'se#0#0';
const live = p => p.evaluate(({ c, k }) => ((window.__fbStore['rooms'][c] || {}).bp2Live || {})[k] || null, { c: CODE, k: KEY });
// egy elem közvetlen szám-gyermekei (CupCounter értékek): fontSize 28 (host) / 26 (obs)
const cupNums = (p, sel) => p.evaluate(s => [...document.querySelectorAll(s + ' div')].filter(d => d.children.length === 0 && /^\d+$/.test((d.textContent||'').trim()) && (getComputedStyle(d).fontSize === '28px' || getComputedStyle(d).fontSize === '26px')).map(d => d.textContent.trim()), sel);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1700 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ code }) => {
    const pl = [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 }];
    window.__fbStore['rooms'] = { [code]: { code, players: pl, gameIdx: 0, selectedGames: ['beerpong2'] } };
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:850px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      gameMeta: { beerpong2Config: { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:5, thirdPlace:false } },
      onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
    const f = document.createElement('div'); f.id = '__obs';
    f.style.cssText = 'position:absolute;left:0;top:860px;width:402px;height:820px;overflow:auto;z-index:9;background:#fff';
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

  // ── 1. Host elindítja a meccset ──
  console.log('\n===== 1. HOST START =====');
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__host button')].find(x => /^▶\s*Start/.test((x.textContent||'').trim())); if (b) b.click(); });
  await p.waitForTimeout(500);
  ok(!!(await live(p)), 'a meccs elindult (bp2Live megvan)', JSON.stringify(await live(p)));

  // ── 2. Host beírja: p1 +3 → közös bp2Live.c1 = 3, az observer is látja ──
  console.log('\n===== 2. HOST POHÁR → OBSERVER =====');
  for (let i = 0; i < 3; i++) { await p.evaluate(() => { const bs = [...document.querySelectorAll('#__host button')].filter(x => (x.textContent||'').trim() === '+'); if (bs[0]) bs[0].click(); }); await p.waitForTimeout(120); }
  await p.waitForTimeout(400);
  ok((await live(p)).c1 === 3, '⚠️ a host beírt pohara a KÖZÖS bp2Live.c1-be került (=3)', (await live(p)).c1);
  const obsNums = await cupNums(p, '#__obs');
  ok(obsNums.includes('3'), '⚠️ az observer LÁTJA a host által beírt 3-at', JSON.stringify(obsNums));

  // ── 3. Observer beírja: p2 +2 → bp2Live.c2 = 2, a host is látja ──
  console.log('\n===== 3. OBSERVER POHÁR → HOST =====');
  for (let i = 0; i < 2; i++) { await p.evaluate(() => { const bs = [...document.querySelectorAll('#__obs button')].filter(x => (x.textContent||'').trim() === '+'); if (bs[1]) bs[1].click(); }); await p.waitForTimeout(150); }
  await p.waitForTimeout(500);
  ok((await live(p)).c2 === 2, '⚠️ az observer beírt pohara a bp2Live.c2-be került (=2)', (await live(p)).c2);
  const hostNums = await cupNums(p, '#__host');
  ok(hostNums.includes('2') && hostNums.includes('3'), '⚠️ a host is LÁTJA az observer 2-esét (a fő kártyán 3 és 2)', JSON.stringify(hostNums));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
