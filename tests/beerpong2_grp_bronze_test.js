// v10.397 — Beer Pong 2.0: 3. helyért (bronz) a Csoport → Kieséses (grp_rr_se) formátumban is
//
// A 3. helyért meccs eddig CSAK tiszta SE-nél élt (THIRD_PLACE gate: TOURNAMENT==='se').
// A grp_rr_se döntője szintén kieséses ág, ezért a bronz ott is értelmes — mostantól
// a wizard kapcsoló megjelenik, a motor pedig a döntő SE-ágán is elindítja a bronzot.
//
// Fogódzó (grp_rr_se, 4 fő, 2 csoport × 2, groupAdvance:2 → mind a 4 továbbjut a
// 4-fős SE döntőbe, thirdPlace:true):
//  1) csoportkör lezárása → SE döntő fázis, 2 elődöntővel
//  2) a 2 elődöntő + a döntő lezárása NEM hirdet azonnal bajnokot — a BRONZ indul
//  3) a bronz lezárása → bajnok + 🥇🥈🥉 rangsor
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990397';
const bpState = p => p.evaluate(c => window.__fbStore['rooms'][c].bp2State || {}, CODE);
const hostTxt = p => p.evaluate(() => (document.getElementById('__host').innerText || '').replace(/\s+/g, ' '));
const clickHost = (p, re) => p.evaluate(reSrc => { const b = [...document.querySelectorAll('#__host button')].find(x => new RegExp(reSrc).test(x.textContent || '')); if (b) { b.click(); return true; } return false; }, re.source);
const clickAllHost = async (p, re, times) => { for (let i = 0; i < times; i++) { await clickHost(p, re); await p.waitForTimeout(700); } };

// A jelenlegi függő CSOPORT-meccsek pozíció-alapú mk-kulccsal
const groupPending = p => p.evaluate(c => {
  const bp = window.__fbStore['rooms'][c].bp2State;
  const gs = bp.tsGroups ? (Array.isArray(bp.tsGroups) ? bp.tsGroups : Object.values(bp.tsGroups)) : [];
  const out = [];
  gs.forEach((g, gi) => { if (!g || g.done) return; const ms = Array.isArray(g.matches) ? g.matches : Object.values(g.matches || {});
    ms.forEach((m, mi) => { if (m && m.p1 && m.p2 && m.winner == null && !m.draw) out.push({ mk: 'g#' + gi + '#' + mi, p1id: m.p1.id, p2id: m.p2.id, p1name: m.p1.name, p2name: m.p2.name }); }); });
  return out;
}, CODE);
// A jelenlegi kör függő SE-meccsei pozíció-alapú mk-kulccsal
const sePending = p => p.evaluate(c => {
  const bp = window.__fbStore['rooms'][c].bp2State;
  const rObj = bp.seRounds; const rnd = bp.seCurRound ?? 0;
  const r0 = Array.isArray(rObj) ? rObj[rnd] : Object.values(rObj)[rnd];
  const arr = Array.isArray(r0) ? r0 : Object.values(r0);
  return arr.map((m, i) => ({ m, i })).filter(({ m }) => m && m.p1 && m.p2 && m.winner == null && !m.tbd).map(({ m, i }) => ({ mk: 'se#' + rnd + '#' + i, p1id: m.p1.id, p2id: m.p2.id, p1name: m.p1.name, p2name: m.p2.name }));
}, CODE);
const submitAll = (p, subs) => p.evaluate(({ code, subs }) => {
  const ref = firebase.firestore().collection('rooms').doc(code);
  const map = {};
  subs.forEach(s => { map[s.mk] = { mk: s.mk, p1id: s.p1id, p2id: s.p2id, p1name: s.p1name, p2name: s.p2name, p1: s.p1, p2: s.p2, by: s.by, ts: Date.now() + Math.random() }; });
  return ref.set({ bp2Submit: map }, { merge: true });
}, { code: CODE, subs });

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1800 } });
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
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:1000px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      // grp_rr_se, 2 csoport × 2 fő, mind a 4 tovabbjut → 4-fos SE donto, thirdPlace BE
      gameMeta: { beerpong2Config: { tournamentType:'grp_rr_se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:0, numGroups:2, groupAdvance:2, thirdPlace:true } },
      onAdvance: (dm, pm) => { window.__adv = { dm, pm }; }, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
  }, { code: CODE });
  await p.waitForTimeout(1800);

  // ── 1. Csoportkör → SE döntő ──
  console.log('\n===== 1. CSOPORTKÖR → SE DÖNTŐ =====');
  const st0 = await bpState(p);
  ok(st0.phase === 'groups', 'a torna csoport-fázisban indul', st0.phase);
  ok(st0.thirdPlace === true, '⚠️ a bp2State thirdPlace=true (grp_rr_se-ben is)', st0.thirdPlace);
  const gp = await groupPending(p);
  ok(gp.length === 2, '2 csoport → 2 függő csoport-meccs', gp.length);
  // mindkét csoportban p1 nyer 10–5
  await submitAll(p, gp.map(s => ({ ...s, p1:10, p2:5, by:'csoport' })));
  await p.waitForTimeout(700);
  await clickAllHost(p, /Elfogadom és rögzítem/, 2);
  await p.waitForTimeout(500);
  const st1 = await bpState(p);
  ok(st1.phase === 'finals', '⚠️ a csoportkör után a döntő (finals) fázis indul', st1.phase);
  const semis = await sePending(p);
  ok(semis.length === 2, 'a döntő SE-ága 2 elődöntővel indul (4 továbbjutó)', semis.length);

  // ── 2. Elődöntők + döntő → a BRONZ indul (nincs még bajnok) ──
  console.log('\n===== 2. ELŐDÖNTŐK + DÖNTŐ → BRONZ INDUL =====');
  const bronzeLosers = [semis[0].p2id, semis[1].p2id];
  await submitAll(p, semis.map(s => ({ ...s, p1:10, p2:6, by:'elődöntő' })));
  await p.waitForTimeout(700);
  await clickAllHost(p, /Elfogadom és rögzítem/, 2);
  await p.waitForTimeout(500);
  const finals = await sePending(p);
  ok(finals.length === 1, 'a döntő beállt (1 meccs)', finals.length);
  await submitAll(p, [{ ...finals[0], p1:10, p2:7, by:'döntő' }]);
  await p.waitForTimeout(700);
  await clickAllHost(p, /Elfogadom és rögzítem/, 1);
  await p.waitForTimeout(500);
  const st2 = await bpState(p);
  ok(!st2.champion, '⚠️ a döntő után MÉG NINCS bajnok (a bronz hátravan)', st2.champion ? st2.champion.name : 'nincs');
  ok(!!st2.bronze && !st2.bronze.winner, '⚠️ a BRONZ-meccs aktív (grp_rr_se-ben is)', st2.bronze ? 'igen' : 'nincs');
  const bParts = st2.bronze ? [st2.bronze.p1.id, st2.bronze.p2.id].sort() : [];
  ok(bParts.join(',') === bronzeLosers.slice().sort().join(','), 'a bronzban a két elődöntő-vesztes van', bParts.join(','));
  ok(/3\. HELYÉRT|3\. helyért/i.test(await hostTxt(p)), 'a host „3. helyért" címkét mutat');

  // ── 3. A bronz lezárása → bajnok + rangsor ──
  console.log('\n===== 3. BRONZ → BAJNOK + RANGSOR =====');
  await submitAll(p, [{ mk:'bronze', p1id: st2.bronze.p1.id, p2id: st2.bronze.p2.id, p1name: st2.bronze.p1.name, p2name: st2.bronze.p2.name, p1:10, p2:5, by:'bronz' }]);
  await p.waitForTimeout(700);
  await clickAllHost(p, /Elfogadom és rögzítem/, 1);
  await p.waitForTimeout(700);
  const st3 = await bpState(p);
  ok(!!st3.champion && st3.champion.id === finals[0].p1id, `a bajnok a döntő nyertese (${finals[0].p1name})`, st3.champion && st3.champion.name);
  const ht = await hostTxt(p);
  ok(/Végeredmény/i.test(ht), 'a champion-képernyő kiírja a Végeredményt');
  ok(/🥇/.test(ht) && /🥈/.test(ht) && /🥉/.test(ht), '⚠️ arany/ezüst/bronz érem mind kint van (grp_rr_se rangsor)');
  const adv = await p.evaluate(() => window.__adv);
  ok(adv && adv.pm && adv.pm[finals[0].p1id] > 0, 'a bajnok pontot kap (onAdvance a bronz UTÁN)', adv && JSON.stringify(adv.pm));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
