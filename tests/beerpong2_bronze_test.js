// v10.379 — Beer Pong 2.0: 3. helyért meccs (bronz) + végső rangsor
//
// A döntő után a két elődöntő-vesztes játszik a 3. helyért; a bajnokot addig
// VISSZATARTJUK (pendingChampRef), és csak a bronz lezárása után hirdetjük ki,
// a teljes rangsorral (1-2-3-4). A bronz ugyanazon a telefonos beküldés + host
// jóváhagyás úton megy, mint a többi meccs.
//
// Fogódzók (4 játékos, thirdPlace alapból BE):
//  1) a 2 elődöntő lezárása után a döntő jön
//  2) a döntő lezárása NEM hirdet bajnokot — a BRONZ indul (a 2 elődöntő-vesztes)
//  3) a bronz lezárása után van bajnok, ÉS a végeredmény 1-2-3-4 helyes
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990033';
const bpState = p => p.evaluate(c => window.__fbStore['rooms'][c].bp2State || {}, CODE);
const hostTxt = p => p.evaluate(() => (document.getElementById('__host').innerText || '').replace(/\s+/g, ' '));
const phoneTxt = p => p.evaluate(() => (document.getElementById('__phone').innerText || '').replace(/\s+/g, ' '));
const clickHost = (p, re) => p.evaluate(reSrc => { const b = [...document.querySelectorAll('#__host button')].find(x => new RegExp(reSrc).test(x.textContent || '')); if (b) { b.click(); return true; } return false; }, re.source);
const clickAllHost = async (p, re, times) => { for (let i = 0; i < times; i++) { await clickHost(p, re); await p.waitForTimeout(700); } };
const roundMatches = p => p.evaluate(c => {
  const bp = window.__fbStore['rooms'][c].bp2State;
  const rObj = bp.seRounds; const r0 = Array.isArray(rObj) ? rObj[bp.seCurRound ?? 0] : Object.values(rObj)[bp.seCurRound ?? 0];
  const arr = Array.isArray(r0) ? r0 : Object.values(r0);
  return arr.filter(m => m && m.p1 && m.p2 && m.winner == null).map(m => ({ p1id: m.p1.id, p2id: m.p2.id, p1name: m.p1.name, p2name: m.p2.name }));
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
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:940px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      gameMeta: { beerpong2Config: { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:0, tables:2 } }, // thirdPlace alapból BE
      onAdvance: (dm, pm) => { window.__adv = { dm, pm }; }, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
    const f = document.createElement('div'); f.id = '__phone';
    f.style.cssText = 'position:absolute;left:0;top:960px;width:402px;height:720px;overflow:auto;z-index:9;background:#fff';
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

  // ── 1. Elődöntők → döntő ──
  console.log('\n===== 1. ELŐDÖNTŐK → DÖNTŐ =====');
  const semis = await roundMatches(p);
  ok(semis.length === 2, 'a 0. kör 2 elődöntő', semis.length);
  // semi0: p1 nyer 10–6 (vesztes: semi0.p2) ; semi1: p1 nyer 10–4 (vesztes: semi1.p2)
  await submitAll(p, [{ ...semis[0], p1:10, p2:6, by:'A' }, { ...semis[1], p1:10, p2:4, by:'B' }]);
  await p.waitForTimeout(700);
  await clickAllHost(p, /Elfogadom és rögzítem/, 2);
  const finals = await roundMatches(p);
  ok(finals.length === 1, 'a döntő beállt (1 meccs)', finals.length);
  const bronzeLosers = [semis[0].p2id, semis[1].p2id];

  // ── 2. A döntő lezárása NEM hirdet bajnokot — a BRONZ indul ──
  console.log('\n===== 2. DÖNTŐ → A BRONZ INDUL (nincs még bajnok) =====');
  await submitAll(p, [{ ...finals[0], p1:10, p2:7, by:'döntő' }]);
  await p.waitForTimeout(700);
  await clickAllHost(p, /Elfogadom és rögzítem/, 1);
  const st1 = await bpState(p);
  ok(!st1.champion, '⚠️ a döntő után MÉG NINCS bajnok (a bronz hátravan)', st1.champion ? st1.champion.name : 'nincs');
  ok(!!st1.bronze && !st1.bronze.winner, 'a bronz-meccs aktív', st1.bronze ? 'igen' : 'nincs');
  const bParts = st1.bronze ? [st1.bronze.p1.id, st1.bronze.p2.id].sort() : [];
  ok(bParts.join(',') === bronzeLosers.slice().sort().join(','), 'a bronzban a két elődöntő-vesztes van', bParts.join(','));
  ok(/3\. HELYÉRT|3\. helyért/i.test(await hostTxt(p)), 'a host „3. helyért" címkét mutat', /HELYÉRT/i.test(await hostTxt(p)));
  ok(/Elfogadom és rögzítem/.test(await hostTxt(p)) || /Néző|3/.test(await phoneTxt(p)), 'a bronz beküldhető (host/telefon)');

  // ── 3. A bronz lezárása → bajnok + végső rangsor ──
  console.log('\n===== 3. BRONZ → BAJNOK + RANGSOR =====');
  // bronz p1 nyer 10–5 → bronz p1 = 3. hely, bronz p2 = 4. hely
  await submitAll(p, [{ p1id: st1.bronze.p1.id, p2id: st1.bronze.p2.id, p1name: st1.bronze.p1.name, p2name: st1.bronze.p2.name, p1:10, p2:5, by:'bronz' }]);
  await p.waitForTimeout(700);
  await clickAllHost(p, /Elfogadom és rögzítem/, 1);
  await p.waitForTimeout(700);
  const st2 = await bpState(p);
  ok(!!st2.champion && st2.champion.id === finals[0].p1id, `a bajnok a döntő nyertese (${finals[0].p1name})`, st2.champion && st2.champion.name);
  const ht = await hostTxt(p);
  ok(/Végeredmény/i.test(ht), 'a champion-képernyő kiírja a Végeredményt', /Végeredmény/i.test(ht));
  // mind a 4 játékos szerepel a rangsorban
  ok(['Sere','Kecsi','Vivi','Robi'].every(n => ht.includes(n)), 'mind a 4 játékos a rangsorban van');
  // a bronz nyertese a 3. (🥉), a bronz vesztese a 4.
  ok(/🥇/.test(ht) && /🥈/.test(ht) && /🥉/.test(ht), 'arany/ezüst/bronz érem mind kint van');
  const adv = await p.evaluate(() => window.__adv);
  ok(adv && adv.pm && adv.pm[finals[0].p1id] > 0, 'a bajnok pontot kap (onAdvance a bronz UTÁN)', adv && JSON.stringify(adv.pm));
  ok(adv && adv.dm && adv.dm[st1.bronze.p2.id] >= 5, 'a bronz vesztese is kapott kortyot a végső könyvelésben', adv && adv.dm && adv.dm[st1.bronze.p2.id]);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
