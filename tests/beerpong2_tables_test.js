// v10.378 — Beer Pong 2.0: PÁRHUZAMOS ASZTALOK
//
// A kieséses kör több meccse mehet EGYSZERRE, telefonról beküldve; a host
// mindegyiket külön jóváhagyja. A `bp2Submit` MAP (kulcs a két játékos id-je),
// így több asztal beküldése egyszerre megfér. A `handleSEConfirm` explicit
// cups-szal TETSZŐLEGES függőben lévő meccset lezár (nem csak a mutatót).
//
// Fogódzók (4 játékos, 2 asztal → a 0. kör 2 elődöntő):
//  1) a telefon 2 beküldő-kártyát mutat (párhuzamos asztalok)
//  2) két egyidejű beküldés → a host 2 jóváhagyó kártyát mutat
//  3) mindkettő elfogadása lezárja a két elődöntőt (out-of-order is jó),
//     mindkét vesztes a pohár-különbséget issza, és a kör a DÖNTŐRE lép
//  4) a döntő rögzítése bajnokot hirdet, a bajnok pontot kap
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990022';
const bpState = p => p.evaluate(c => window.__fbStore['rooms'][c].bp2State || {}, CODE);
const hostBtns = (p, re) => p.evaluate(reSrc => [...document.querySelectorAll('#__host button')].filter(b => new RegExp(reSrc).test(b.textContent || '')).length, re.source);
const clickHost = (p, re) => p.evaluate(reSrc => { const b = [...document.querySelectorAll('#__host button')].find(x => new RegExp(reSrc).test(x.textContent || '')); if (b) { b.click(); return true; } return false; }, re.source);

// A 0. kör összes (p1,p2)-vel bíró meccse
const roundMatches = p => p.evaluate(c => {
  const bp = window.__fbStore['rooms'][c].bp2State;
  const rnd = bp.seCurRound ?? 0;
  const rObj = bp.seRounds; const r0 = Array.isArray(rObj) ? rObj[rnd] : Object.values(rObj)[rnd];
  const arr = Array.isArray(r0) ? r0 : Object.values(r0);
  return arr.map((m, i) => ({ m, i })).filter(({ m }) => m && m.p1 && m.p2 && m.winner == null).map(({ m, i }) => ({ mk: 'se#' + rnd + '#' + i, p1id: m.p1.id, p2id: m.p2.id, p1name: m.p1.name, p2name: m.p2.name }));
}, CODE);

// Két/egy beküldés a szoba bp2Submit MAP-jébe (POZÍCIÓ-alapú kulcs — mint a valós observer)
const submitAll = (p, subs) => p.evaluate(({ code, subs }) => {
  const ref = firebase.firestore().collection('rooms').doc(code);
  const map = {};
  subs.forEach(s => { map[s.mk] = { mk: s.mk, p1id: s.p1id, p2id: s.p2id, p1name: s.p1name, p2name: s.p2name, p1: s.p1, p2: s.p2, by: s.by, ts: Date.now() + Math.random() }; });
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
      gameMeta: { beerpong2Config: { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:0, tables:2, thirdPlace:false } },
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

  // ── 1. A 0. kör 2 elődöntő; a telefon 2 beküldő-kártyát mutat ──
  console.log('\n===== 1. PÁRHUZAMOS ASZTALOK — 2 aktív meccs =====');
  const semis = await roundMatches(p);
  ok(semis.length === 2, 'a 0. kör 2 meccs (2 elődöntő)', semis.length);
  const phoneCards = await p.evaluate(() => [...document.querySelectorAll('#__phone button')].filter(b => /Beküldés a hostnak|Állítsd be az eredményt/.test(b.textContent || '')).length);
  ok(phoneCards === 2, 'a telefon 2 beküldő-kártyát mutat', phoneCards);

  // ── 2. Két egyidejű beküldés → host 2 jóváhagyó kártya ──
  console.log('\n===== 2. KÉT EGYIDEJŰ BEKÜLDÉS =====');
  // semi0: p1 nyer 10–6 (vesztes 4-et iszik); semi1: p1 nyer 10–4 (vesztes 6-ot iszik)
  await submitAll(p, [
    { ...semis[0], p1:10, p2:6, by:'1. asztal' },
    { ...semis[1], p1:10, p2:4, by:'2. asztal' },
  ]);
  await p.waitForTimeout(700);
  ok(await hostBtns(p, /Elfogadom és rögzítem/) === 2, 'a host 2 jóváhagyó kártyát mutat', await hostBtns(p, /Elfogadom és rögzítem/));

  // ── 3. Mindkettő elfogadása → két elődöntő lezárul, döntőre lép ──
  console.log('\n===== 3. MINDKETTŐ ELFOGADÁSA =====');
  await clickHost(p, /Elfogadom és rögzítem/); await p.waitForTimeout(700);
  await clickHost(p, /Elfogadom és rögzítem/); await p.waitForTimeout(900);
  const st = await bpState(p);
  ok(!st.champion, 'még nincs bajnok (a döntő hátravan)', st.champion ? st.champion.name : 'nincs');
  ok(st.drinkMap[semis[0].p2id] === 4, `az 1. elődöntő vesztese (${semis[0].p2name}) 4 kortyot ivott`, st.drinkMap[semis[0].p2id]);
  ok(st.drinkMap[semis[1].p2id] === 6, `a 2. elődöntő vesztese (${semis[1].p2name}) 6 kortyot ivott`, st.drinkMap[semis[1].p2id]);
  ok(await hostBtns(p, /Elfogadom és rögzítem/) === 0, 'a jóváhagyó kártyák eltűntek (nincs több beküldés)');
  const finals = await roundMatches(p);
  ok(finals.length === 1, 'a következő kör 1 meccs — a döntő', finals.length);

  // ── 4. A döntő rögzítése → bajnok + pont ──
  console.log('\n===== 4. A DÖNTŐ =====');
  await submitAll(p, [{ ...finals[0], p1:10, p2:7, by:'döntő' }]);
  await p.waitForTimeout(700);
  await clickHost(p, /Elfogadom és rögzítem/); await p.waitForTimeout(1200);
  const st2 = await bpState(p);
  ok(!!st2.champion && st2.champion.id === finals[0].p1id, `a bajnok a döntő nyertese (${finals[0].p1name})`, st2.champion && st2.champion.name);
  const adv = await p.evaluate(() => window.__adv);
  ok(adv && adv.pm && adv.pm[finals[0].p1id] > 0, 'a bajnok pontot kap (onAdvance pm)', adv && JSON.stringify(adv.pm));
  ok(adv && adv.dm && adv.dm[finals[0].p2id] === 3, `a döntő vesztese (${finals[0].p2name}) 3 kortyot kap`, adv && adv.dm && JSON.stringify(adv.dm));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
