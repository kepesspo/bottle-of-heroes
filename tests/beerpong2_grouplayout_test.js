// v10.393 — Beer Pong 2.0 observer: csoportok EGYMÁS MELLETT + szélesebb jobb sáv;
// host: a csoport-állásból NEM indítható meccs (a ▶ strip kikerült — redundáns volt).
//
// Fogódzók (grp_rr, 2 csoport, nagy kijelző):
//  1) az observer „Csoportkör" blokkjában a két csoport-állás EGYMÁS MELLETT van
//  2) a jobb oldali sáv (Pohár összesítő) szélesebb (~264, nem 200)
//  3) a host csoport-állás kártyáján NINCS ▶ indító (a match-listában van)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990393';

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1360, height: 1000 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
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
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:1200px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      gameMeta: { beerpong2Config: { tournamentType:'grp_rr_se', mode:'egyeni', maxCups:10, finalCups:10, matchMinutes:5, numGroups:2, groupAdvance:1, thirdPlace:false } },
      onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
    const f = document.createElement('div'); f.id = '__obs';
    f.style.cssText = 'position:absolute;left:410px;top:0;width:1180px;height:1000px;overflow:auto;z-index:9;background:#fff';
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

  // ── 1. Observer: a két csoport-állás EGYMÁS MELLETT ──
  console.log('\n===== 1. CSOPORTOK EGYMÁS MELLETT (observer) =====');
  const groups = await p.evaluate(() => {
    const labels = [...document.querySelectorAll('#__obs *')].filter(n => /^[AB]\s*csoport/i.test((n.textContent||'').trim()) && n.children.length <= 2);
    // a legkonkrétabb (legkisebb) A és B fejléc
    const a = labels.find(n => /^A\s*csoport/i.test(n.textContent.trim()));
    const bb = labels.find(n => /^B\s*csoport/i.test(n.textContent.trim()));
    if (!a || !bb) return { found:false };
    const ra = a.getBoundingClientRect(), rb = bb.getBoundingClientRect();
    return { found:true, sameRow: Math.abs(ra.top - rb.top) < 40, sideBySide: Math.abs(ra.left - rb.left) > 120 };
  });
  ok(groups.found, 'megvan az A és B csoport fejléc', JSON.stringify(groups));
  ok(groups.sameRow && groups.sideBySide, '⚠️ a két csoport EGYMÁS MELLETT van (azonos sor, eltérő oszlop)', JSON.stringify(groups));

  // ── 2. Jobb oldali sáv szélesebb (~264) ──
  console.log('\n===== 2. SZÉLESEBB JOBB SÁV =====');
  const sidebarW = await p.evaluate(() => {
    const hdr = [...document.querySelectorAll('#__obs *')].find(n => /^🍺\s*Pohár összesítő$/i.test((n.textContent||'').trim()) && n.children.length === 0);
    if (!hdr) return 0;
    // a panel a fejléc szülője
    return hdr.parentElement.getBoundingClientRect().width;
  });
  ok(sidebarW > 240, '⚠️ a jobb sáv szélesebb, mint 240px (nem a régi 200)', Math.round(sidebarW));

  // ── 3. Host: a csoport-állás kártyáján NINCS ▶ indító ──
  console.log('\n===== 3. HOST — NINCS ▶ A CSOPORT-ÁLLÁSBAN =====');
  const noStrip = await p.evaluate(() => {
    // a csoport-áttekintő kártya fejléce: „<label> állás"
    const cards = [...document.querySelectorAll('#__host div')].filter(d => /csoport állás/i.test(d.textContent || ''));
    // a legkisebb ilyen kártya (a group-overview standings kártya)
    cards.sort((a,b) => a.textContent.length - b.textContent.length);
    const card = cards[0];
    if (!card) return { noCard:true };
    // van-e ▶ gomb ezen a kártyán belül?
    const hasPlay = [...card.querySelectorAll('button')].some(btn => (btn.textContent||'').trim() === '▶');
    return { hasPlay };
  });
  ok(!noStrip.noCard, 'megvan a host csoport-állás kártya', JSON.stringify(noStrip));
  ok(noStrip.hasPlay === false, '⚠️ a csoport-állás kártyán NINCS ▶ indító (redundancia kivezetve)', JSON.stringify(noStrip));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
