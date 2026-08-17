// v10.387 — Beer Pong 2.0: PÁRHUZAMOS elfogadás RR/CSOPORT módban is
//
// A bejelentett HIBA (két rész):
//  1) „az observer beküldött 2 meccset, de csak 1-et tudok elfogadni a hoston" —
//     RR/csoport módban a host csak a MUTATÓ meccs beküldését fogadta el.
//  2) „csak az 1 csapat meccsei indíthatóak" — az observer csak a SOROS csoport
//     meccseit mutatta (nem az összesét).
//
// Javítás (v10.387): a host BÁRMELYIK függő meccs beküldését elfogadja (explicit
// cups, id-alapú koordináta), és az observer MINDEN csoport függő meccsét mutatja.
//
// Fogódzó: grp_rr_se, 2 csoport (2-2 fő) → 2 csoport-meccs, mindkettő függő.
//  1) az observer MINDKÉT csoport meccsét mutatja (2 beküldő-kártya) — #2
//  2) mindkettő beküldve → a host 2 jóváhagyó kártyát mutat — #1 (látja)
//  3) MINDKETTŐ elfogadható → mindkét vesztes iszik, a torna a döntőre lép — #1
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990387';
const bpState = p => p.evaluate(c => (window.__fbStore['rooms'][c] || {}).bp2State || {}, CODE);
const hostBtns = (p, re) => p.evaluate(reSrc => [...document.querySelectorAll('#__host button')].filter(b => new RegExp(reSrc).test(b.textContent || '')).length, re.source);
const clickHost = (p, re) => p.evaluate(reSrc => { const b = [...document.querySelectorAll('#__host button')].find(x => new RegExp(reSrc).test(x.textContent || '')); if (b) { b.click(); return true; } return false; }, re.source);

// Minden csoport összes függő (p1,p2)-vel bíró meccse
const groupMatches = p => p.evaluate(c => {
  const bp = window.__fbStore['rooms'][c].bp2State;
  const groups = bp.tsGroups ? (Array.isArray(bp.tsGroups) ? bp.tsGroups : Object.values(bp.tsGroups)) : [];
  const out = [];
  groups.forEach(g => {
    const ms = Array.isArray(g.matches) ? g.matches : Object.values(g.matches || {});
    ms.forEach(m => { if (m && m.p1 && m.p2 && m.winner == null && !m.draw) out.push({ p1id: m.p1.id, p2id: m.p2.id, p1name: m.p1.name, p2name: m.p2.name }); });
  });
  return out;
}, CODE);

const submitAll = (p, subs) => p.evaluate(({ code, subs }) => {
  const ref = firebase.firestore().collection('rooms').doc(code);
  const map = {};
  subs.forEach(s => { map[s.p1id + '__' + s.p2id] = { p1id: s.p1id, p2id: s.p2id, p1name: s.p1name, p2name: s.p2name, p1: s.p1, p2: s.p2, by: s.by, ts: Date.now() + Math.random() }; });
  return ref.set({ bp2Submit: map }, { merge: true });
}, { code: CODE, subs });

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
      // 2 csoport, 2-2 fo → 2 csoport-meccs, mindketto fuggo
      gameMeta: { beerpong2Config: { tournamentType:'grp_rr_se', mode:'egyeni', maxCups:10, finalCups:10, matchMinutes:5, numGroups:2, groupAdvance:1, thirdPlace:false } },
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

  // ── 1. Két csoport, két függő meccs; az observer MINDKETTŐT mutatja ──
  console.log('\n===== 1. MINDEN CSOPORT MECCSE LÁTSZIK (nem csak a soros) =====');
  const st0 = await bpState(p);
  ok(st0.phase === 'groups', 'a torna csoport-fázisban indul', st0.phase);
  const gm = await groupMatches(p);
  ok(gm.length === 2, '2 csoport → 2 függő csoport-meccs', gm.length);
  const phoneCards = await p.evaluate(() => [...document.querySelectorAll('#__phone button')].filter(b => /Beküldés a hostnak|Állítsd be az eredményt/.test(b.textContent || '')).length);
  ok(phoneCards === 2, '⚠️ az observer MINDKÉT csoport meccsét mutatja (nem csak a soros csoportét)', phoneCards);

  // ── 2. Két beküldés → a host 2 jóváhagyó kártyát mutat ──
  console.log('\n===== 2. KÉT BEKÜLDÉS → A HOST MINDKETTŐT LÁTJA =====');
  await submitAll(p, [
    { ...gm[0], p1:10, p2:6, by:'A csoport' },
    { ...gm[1], p1:10, p2:4, by:'B csoport' },
  ]);
  await p.waitForTimeout(700);
  ok(await hostBtns(p, /Elfogadom és rögzítem/) === 2, '⚠️ a host 2 jóváhagyó kártyát mutat (nem csak 1-et)', await hostBtns(p, /Elfogadom és rögzítem/));

  // ── 3. MINDKETTŐ elfogadható → mindkét vesztes iszik, döntőre lép ──
  console.log('\n===== 3. MINDKETTŐ ELFOGADHATÓ =====');
  await clickHost(p, /Elfogadom és rögzítem/); await p.waitForTimeout(700);
  await clickHost(p, /Elfogadom és rögzítem/); await p.waitForTimeout(900);
  const st1 = await bpState(p);
  ok(st1.drinkMap[gm[0].p2id] === 4, `az A csoport vesztese (${gm[0].p2name}) 4 kortyot ivott`, st1.drinkMap[gm[0].p2id]);
  ok(st1.drinkMap[gm[1].p2id] === 6, `a B csoport vesztese (${gm[1].p2name}) 6 kortyot ivott`, st1.drinkMap[gm[1].p2id]);
  ok(await hostBtns(p, /Elfogadom és rögzítem/) === 0, 'a jóváhagyó kártyák eltűntek (mindkettő rögzítve)');
  ok(st1.phase === 'finals', 'a csoportok után a döntő (finals) indul', st1.phase);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
