// v10.394 — Beer Pong 2.0: TÖBBSZÖRÖS leg (ugyanaz a páros többször játszik)
//
// A bejelentett HIBA: ha egy csoportban 3× játszanak egymással a játékosok
// (rrLegs=3), a csupasz `p1__p2` kulcs ütközött → 1 meccshez 2× írtunk eredményt,
// és a beküldés elfogadása után nem tűnt el a meccs. Javítás: POZÍCIÓ-alapú kulcs
// (`g#<gi>#<mi>`), így a PONTOS leget azonosítjuk.
//
// Fogódzó: 1 csoport, 3 játékos, rrLegs=3 → 9 meccs, minden páros 3×. Beküldünk EGY
// konkrét leget → csak AZ a meccs zárul le, a páros többi lege függő marad, és a
// beküldés eltűnik.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990394';
const hostBtns = (p, re) => p.evaluate(reSrc => [...document.querySelectorAll('#__host button')].filter(b => new RegExp(reSrc).test(b.textContent || '')).length, re.source);
const clickHost = (p, re) => p.evaluate(reSrc => { const b = [...document.querySelectorAll('#__host button')].find(x => new RegExp(reSrc).test(x.textContent || '')); if (b) { b.click(); return true; } return false; }, re.source);

// A 0. csoport összes meccse mk-kulccsal + a győztes id-je (vagy null)
const g0matches = p => p.evaluate(c => {
  const bp = window.__fbStore['rooms'][c].bp2State;
  const groups = bp.tsGroups ? (Array.isArray(bp.tsGroups) ? bp.tsGroups : Object.values(bp.tsGroups)) : [];
  const g = groups[0]; const ms = Array.isArray(g.matches) ? g.matches : Object.values(g.matches || {});
  return ms.map((m, mi) => ({ mk: 'g#0#' + mi, p1id: m.p1 && m.p1.id, p2id: m.p2 && m.p2.id, p1name: m.p1 && m.p1.name, p2name: m.p2 && m.p2.name, winner: m.winner ? m.winner.id : null, pair: [m.p1 && m.p1.id, m.p2 && m.p2.id].sort().join('_') }));
}, CODE);

const submitOne = (p, s, a, bcups) => p.evaluate(({ code, s, a, bcups }) =>
  firebase.firestore().collection('rooms').doc(code).set({ bp2Submit: { [s.mk]: { mk: s.mk, p1id: s.p1id, p2id: s.p2id, p1name: s.p1name, p2name: s.p2name, p1: a, p2: bcups, by: 'asztal', ts: Date.now() } } }, { merge: true }),
  { code: CODE, s, a, bcups });

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1200 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ code }) => {
    const pl = [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
                { id:'p2', name:'Vivi', color:'#A78BFA', points:0, drinks:0 }];
    window.__fbStore['rooms'] = { [code]: { code, players: pl, gameIdx: 0, selectedGames: ['beerpong2'] } };
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:1200px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      // 1 csoport, 3 fő, rrLegs:3 → minden páros 3× játszik (9 meccs)
      gameMeta: { beerpong2Config: { tournamentType:'grp_rr_se', mode:'egyeni', maxCups:10, finalCups:10, matchMinutes:0, numGroups:1, groupAdvance:1, rrLegs:3, thirdPlace:false } },
      onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
  }, { code: CODE });
  await p.waitForTimeout(1600);

  // ── 1. 9 meccs, minden páros 3× ──
  console.log('\n===== 1. TÖBBSZÖRÖS LEG =====');
  const ms0 = await g0matches(p);
  ok(ms0.length === 9, '1 csoport / 3 fő / rrLegs:3 → 9 meccs', ms0.length);
  // válasszunk egy párost, ami többször szerepel
  const byPair = {}; ms0.forEach(m => { (byPair[m.pair] = byPair[m.pair] || []).push(m); });
  const repeated = Object.values(byPair).find(a => a.length >= 3);
  ok(!!repeated, '⚠️ van páros, ami 3× szerepel (KÜLÖNBÖZŐ mk-val)', repeated && repeated.map(m => m.mk).join(', '));
  const uniqueMk = new Set(ms0.map(m => m.mk));
  ok(uniqueMk.size === 9, 'mind a 9 meccs kulcsa EGYEDI (nem ütközik a páros)', uniqueMk.size);

  // ── 2. Beküldjük a páros MÁSODIK legét (g#0#<mid>) ──
  console.log('\n===== 2. EGY KONKRÉT LEG BEKÜLDÉSE + ELFOGADÁS =====');
  const target = repeated[1];   // a páros 2. lege
  await submitOne(p, target, 3, 0);   // p1 nyer 3-0
  await p.waitForTimeout(600);
  ok(await hostBtns(p, /Elfogadom és rögzítem/) === 1, 'a host PONTOSAN 1 jóváhagyó kártyát mutat (nem 3-at a párosra)', await hostBtns(p, /Elfogadom és rögzítem/));
  await clickHost(p, /Elfogadom és rögzítem/); await p.waitForTimeout(800);

  // ── 3. CSAK a beküldött leg zárult le; a többi függő; a beküldés eltűnt ──
  console.log('\n===== 3. CSAK A KONKRÉT LEG ZÁRULT LE =====');
  const ms1 = await g0matches(p);
  const mid = +target.mk.split('#')[2];
  ok(ms1[mid].winner === target.p1id, `a beküldött leg (${target.mk}) lezárult, a győztes ${target.p1name}`, ms1[mid].winner);
  const otherLegs = repeated.filter(m => m.mk !== target.mk).map(m => +m.mk.split('#')[2]);
  ok(otherLegs.every(idx => ms1[idx].winner === null), '⚠️ a páros TÖBBI lege FÜGGŐ maradt (nem zárult le duplán)', otherLegs.map(idx => ms1[idx].winner).join(','));
  ok(await hostBtns(p, /Elfogadom és rögzítem/) === 0, '⚠️ a beküldés ELTŰNT az elfogadás után (nem ragad be)');
  const subLeft = await p.evaluate(c => Object.keys((window.__fbStore['rooms'][c] || {}).bp2Submit || {}).length, CODE);
  ok(subLeft === 0, 'a bp2Submit üres (a leg kulcsa törlődött)', subLeft);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
