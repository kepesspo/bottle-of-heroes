// v10.331 — Blackjack: a telefon gyors koppintásai nem veszhetnek el
//
// A TÜNET: „az observernél nem működnek a gombok". A Hit/Stand néha nem
// csinált semmit — de csak élesben, két készülékkel.
//
// AZ OK: a telefon a LEGUTOLSÓ pillanatképből számolja a következő állapotot
// (`bjDoHit(bj, …)`), a pillanatkép viszont csak a hálózati köridő (100–300 ms)
// után ér vissza. Két gyors koppintás között a második még a RÉGI állapotot
// látta, és a saját írása felülírta az elsőt.
//
// ⚠️ EZ A HIBA CSAK KÉSLELTETÉSSEL LÁTSZIK. A `fbstub` azonnal kézbesít, ezért
// a teszt maga tolja el a pillanatkép-kézbesítést 250 ms-mal — enélkül a régi
// (hibás) kód is átmenne, mint ahogy a fejlesztés közben át is ment.
//
// A JAVÍTÁS: minden írás JELÖLŐT (`echoTok`) kap, a telefon azonnal alkalmazza
// helyben, és csak akkor engedi el, ha a SAJÁT írása ért vissza. Bármelyik
// pillanatképre elengedni kevés: az érkező lehet régebbi, mint amit már
// kiírtunk — pont ez történik két gyors koppintásnál.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'p0', name:'Host', color:'#6FA86F' }, { id:'p1', name:'Márk', color:'#4C8DD8' }];
const DECK = ['4♣','9♦','J♥','3♠','8♣','K♥','2♥','6♦'];
const LAG = 250;   // a valodi halozati korido nagysagrendje

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1200 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ pl, deck, lag }) => {
    window.__fbStore['rooms'] = { '801118': { players: pl, bjTakenIds:['p1'], bjHostPid:'p0',
      bjState: { phase:'playing', gameIdx:0, hostId:'p0', participants:['p1'], deck,
        hands:{ p1:['2♣','3♥'] }, dealerHand:['5♠','K♦'], bets:{ p1:5 }, betsDone:{ p1:true },
        stood:{}, bust:{}, doubled:{}, handKeys:{ p1:['p1'] }, chips:{ p1:20 }, stacks:{ p1:20 },
        startStack:20, currentTurn:'p1', cashedOut:{}, roundsPlayed:0, allowSplit:true, allowDouble:true } } };
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    // HOST tábla — a valódi topológia: ő is figyeli és írja ugyanazt a szobát
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:600px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BlackjackGame, { players: pl, roomCode:'801118',
      gameIdx:0, gameMeta:{}, onAdvance:()=>{}, onSetHideFooter:()=>{}, onLiveDrinkUpdate:()=>{}, onSetBuszSwitch:()=>{} }));
    // TELEFON — a pillanatkép KÉSVE ér ide, mint a valóságban
    const f = document.createElement('div'); f.id = '__phone';
    f.style.cssText = 'position:absolute;left:0;top:600px;width:402px;height:600px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(f);
    function W() {
      const [room, setRoom] = React.useState(() => window.__fbStore['rooms']['801118']);
      React.useEffect(() => firebase.firestore().collection('rooms').doc('801118')
        .onSnapshot(s => { const d = s.data() || null; setTimeout(() => setRoom(d), lag); }), []);
      if (!room) return null;
      return React.createElement(BlackjackObserverView, { room, code:'801118', onLeave:()=>{},
        keepClaimOnUnmount:true, initialPlayerId:'p1', onPlayerIdChange:()=>{}, onSwitchToHost:()=>{} });
    }
    ReactDOM.createRoot(f).render(React.createElement(W));
  }, { pl: PL, deck: DECK, lag: LAG });
  await p.waitForTimeout(2600);

  const hand = () => p.evaluate(() => (window.__fbStore['rooms']['801118'].bjState.hands.p1 || []).slice());
  const hit = () => p.evaluate(() => {
    const x = [...document.querySelectorAll('#__phone button')].find(y => /^Hit$/.test(y.getAttribute('aria-label') || ''));
    if (!x) return 'NINCS'; if (x.disabled) return 'LETILTVA'; x.click(); return 'ok';
  });
  const reset = () => p.evaluate(async (deck) => {
    const cur = window.__fbStore['rooms']['801118'].bjState;
    await firebase.firestore().collection('rooms').doc('801118').update({ bjState: { ...cur,
      phase:'playing', hands:{ p1:['2♣','3♥'] }, deck, stood:{}, bust:{}, currentTurn:'p1' } });
  }, DECK);

  // ── 1. LASSU koppintasok — ez a regi koddal is mukodott ──
  console.log('\n===== 1. LASSU KOPPINTASOK (1 mp) =====');
  for (let i = 0; i < 3; i++) { await hit(); await p.waitForTimeout(1000); }
  const slow = await hand();
  ok(slow.length === 5, 'három lassú Hit → három új lap', slow.join(','));

  // ── 2. GYORS koppintasok — ITT veszett el a koppintas ──
  console.log('\n===== 2. GYORS KOPPINTASOK (150 ms) =====');
  await reset();
  await p.waitForTimeout(LAG + 900);
  const start = await hand();
  ok(start.length === 2, 'visszaálltunk a kiindulásra', start.join(','));
  const taps = [];
  for (let i = 0; i < 3; i++) { taps.push(await hit()); await p.waitForTimeout(150); }
  await p.waitForTimeout(LAG + 1200);
  const fast = await hand();
  ok(taps.every(t => t === 'ok'), 'mindhárom gomb élt a koppintáskor', taps.join(','));
  ok(fast.length === 5, 'három GYORS Hit is három új lapot ad — egyik koppintás sem veszett el',
     fast.join(',') + '  (' + (fast.length - 2) + ' új lap)');
  ok(new Set(fast).size === fast.length, 'nincs kétszer kiosztott lap', fast.join(','));

  // ── 3. a jelolo tenyleg lemegy a szobaba ──
  console.log('\n===== 3. A JELOLO =====');
  const tok = await p.evaluate(() => window.__fbStore['rooms']['801118'].bjState.echoTok);
  ok(typeof tok === 'string' && tok.length > 4, 'minden írás jelölőt (echoTok) visz', tok);
  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));

  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
