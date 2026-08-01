// v10.242 — Blackjack: biztosítás (insurance) + lapszétválasztás (split)
//
// A modell átállt KÉZ-alapúra: az első kéz kulcsa maga a pid, a split-kezeké
// pid+'#1', pid+'#2', … Így a hands/bets/stood/… map-ek alakja nem változott,
// és egy régi (split nélküli) szoba is olvasható marad.
//
// Amit ellenőriz:
//   1. párfelismerés ÉRTÉK szerint (K+10 is pár), split mechanika, ász-split
//   2. re-split 4 kézig, utána tiltva; zseton-fedezet
//   3. split után a 21 NEM Blackjack (1:1, nem 3:2)
//   4. biztosítás összege (a tét fele, 1-re kerekítve), fedezet, kifizetés 2:1
//   5. a biztosítás-fázis csak osztó-Ásznál indul, és osztó-BJ-nél a kör véget ér
//   6. a kör-egyenleg minden kezet + a biztosítást összegzi
//   7. régi, handKeys nélküli állapot változatlanul működik
//   8. a telefonos felület kirajzolja a biztosítást és a több kezet
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const stub = fs.readFileSync(path.join(__dirname, 'fbstub.js'), 'utf8');

let fail = 0;
const ok = (cond, name, extra) => {
  console.log((cond ? '  OK  ' : '  HIBA') + '   ' + name + (extra !== undefined ? '  → ' + extra : ''));
  if (!cond) fail++;
};

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);

  // ── 1. párfelismerés ──
  console.log('\n===== 1. PÁR = AZONOS ÉRTÉK =====');
  const pair = await p.evaluate(() => ({
    eights: bjPairValue(['8♠', '8♥']),
    kingTen: bjPairValue(['K♠', '10♦']),
    queenJack: bjPairValue(['Q♣', 'J♥']),
    aces: bjPairValue(['A♠', 'A♦']),
    nope: bjPairValue(['9♠', '8♥']),
    three: bjPairValue(['8♠', '8♥', '8♦']),
  }));
  ok(pair.eights === 8, '8+8 pár', String(pair.eights));
  ok(pair.kingTen === 10, 'K+10 is pár (érték, nem rang)', String(pair.kingTen));
  ok(pair.queenJack === 10, 'Q+J is pár', String(pair.queenJack));
  ok(pair.aces === 11, 'Ász-pár', String(pair.aces));
  ok(pair.nope === null, '9+8 NEM pár', String(pair.nope));
  ok(pair.three === null, 'három lapból nem lehet split', String(pair.three));

  // ── 2. split mechanika ──
  console.log('\n===== 2. SPLIT =====');
  const split = await p.evaluate(() => {
    const st = {
      participants: ['a', 'b'], deck: ['2♣', '3♣', '4♣', '5♣', '6♣', '7♣'],
      hands: { a: ['8♠', '8♥'], b: ['9♠', '5♥'] }, dealerHand: ['6♦', '9♣'],
      bets: { a: 2, b: 1 }, stood: {}, bust: {}, doubled: {}, chips: { a: 10, b: 10 },
      handKeys: { a: ['a'], b: ['b'] }, fromSplit: {}, aceSplit: {},
      currentTurn: 'a', phase: 'playing', allowSplit: true,
    };
    const ns = bjDoSplit(st, 'a');
    return {
      keys: bjHandsOf(ns, 'a'),
      h1: ns.hands['a'], h2: ns.hands['a#1'],
      bets: { a: ns.bets['a'], a1: ns.bets['a#1'] },
      fromSplit: [!!ns.fromSplit['a'], !!ns.fromSplit['a#1']],
      turn: ns.currentTurn,
      all: bjAllHandKeys(ns),
      untouchedB: ns.hands['b'],
      deckLeft: ns.deck.length,
    };
  });
  ok(JSON.stringify(split.keys) === JSON.stringify(['a', 'a#1']), 'két kéz lett, sorrendben', split.keys.join(','));
  ok(split.h1.length === 2 && split.h2.length === 2, 'mindkét kéz kapott egy második lapot', JSON.stringify([split.h1, split.h2]));
  ok(split.h1[0] === '8♠' && split.h2[0] === '8♥', 'a pár szétvált', JSON.stringify([split.h1[0], split.h2[0]]));
  ok(split.bets.a === 2 && split.bets.a1 === 2, 'az új kéz ugyanakkora tétet kapott', JSON.stringify(split.bets));
  ok(split.fromSplit[0] && split.fromSplit[1], 'mindkét kéz split-jelölt');
  ok(split.turn === 'a', 'a soros kéz az első maradt', split.turn);
  ok(JSON.stringify(split.all) === JSON.stringify(['a', 'a#1', 'b']), 'a kör-sorrend helyes', split.all.join(','));
  ok(JSON.stringify(split.untouchedB) === JSON.stringify(['9♠', '5♥']), 'a másik játékos keze érintetlen');
  ok(split.deckLeft === 4, 'két lap ment el a pakliból', String(split.deckLeft));

  // ── 3. ász-split: kezenként PONTOSAN egy lap ──
  console.log('\n===== 3. ÁSZ-SPLIT =====');
  const aces = await p.evaluate(() => {
    const st = {
      participants: ['a'], deck: ['2♣', '3♣', '4♣', '5♣'],
      hands: { a: ['A♠', 'A♥'] }, dealerHand: ['6♦', '9♣'],
      bets: { a: 1 }, stood: {}, bust: {}, doubled: {}, chips: { a: 10 },
      handKeys: { a: ['a'] }, fromSplit: {}, aceSplit: {},
      currentTurn: 'a', phase: 'playing', allowSplit: true,
    };
    const ns = bjDoSplit(st, 'a');
    return {
      stood: [!!ns.stood['a'], !!ns.stood['a#1']],
      aceMark: [!!ns.aceSplit['a'], !!ns.aceSplit['a#1']],
      lens: [ns.hands['a'].length, ns.hands['a#1'].length],
      phase: ns.phase,
      canSplitAgain: bjCanSplit(ns, 'a', 10),
      canDouble: bjCanDouble(ns, 'a', 10),
    };
  });
  ok(aces.stood[0] && aces.stood[1], 'mindkét ász-kéz automatikusan áll');
  ok(aces.lens[0] === 2 && aces.lens[1] === 2, 'kezenként pontosan egy új lap', JSON.stringify(aces.lens));
  ok(aces.phase === 'dealer', 'nincs több lépés → jön az osztó', aces.phase);
  ok(aces.canSplitAgain === false, 'ász-splitet nem lehet tovább osztani');
  ok(aces.canDouble === false, 'ász-splitre nem lehet duplázni');

  // ── 4. re-split 4 kézig, és a fedezet ──
  console.log('\n===== 4. RE-SPLIT ÉS FEDEZET =====');
  const resplit = await p.evaluate(() => {
    let st = {
      // FONTOS: a bjPop a pakli VÉGÉRŐL vesz — a 8-asoknak hátul kell lenniük
      participants: ['a'], deck: ['2♣', '3♣', '8♠', '8♥', '8♦', '8♣', '8♠', '8♥', '8♦', '8♣'],
      hands: { a: ['8♠', '8♥'] }, dealerHand: ['6♦', '9♣'],
      bets: { a: 1 }, stood: {}, bust: {}, doubled: {}, chips: { a: 10 },
      handKeys: { a: ['a'] }, fromSplit: {}, aceSplit: {},
      currentTurn: 'a', phase: 'playing', allowSplit: true,
    };
    const steps = [];
    for (let i = 0; i < 5; i++) {
      const can = bjCanSplit(st, st.currentTurn, 10);
      steps.push({ hands: bjHandsOf(st, 'a').length, can });
      if (!can) break;
      st = bjDoSplit(st, st.currentTurn);
    }
    // fedezet: 3 zsetonnal, 2-es tettel a masodik kez mar nem fer bele
    const poor = {
      participants: ['a'], deck: ['2♣', '3♣'], hands: { a: ['8♠', '8♥'] }, dealerHand: ['6♦', '9♣'],
      bets: { a: 2 }, stood: {}, bust: {}, doubled: {}, chips: { a: 3 },
      handKeys: { a: ['a'] }, fromSplit: {}, aceSplit: {}, currentTurn: 'a', phase: 'playing', allowSplit: true,
    };
    return { steps, poorCan: bjCanSplit(poor, 'a', 3), offCan: bjCanSplit({ ...poor, chips:{a:20}, allowSplit:false }, 'a', 20) };
  });
  ok(resplit.steps.length === 4 && resplit.steps[3].can === false,
     'legfeljebb 4 kézig oszthat, utána tiltva', JSON.stringify(resplit.steps.map(s => `${s.hands}:${s.can}`)));
  ok(resplit.poorCan === false, '3 zsetonnal, 2-es téttel nincs fedezet a splitre');
  ok(resplit.offCan === false, 'kikapcsolva egyáltalán nem lehet splitelni');

  // ── 5. split után a 21 NEM Blackjack ──
  console.log('\n===== 5. SPLIT UTÁN A 21 NEM BLACKJACK =====');
  const bj21 = await p.evaluate(() => {
    const base = {
      participants: ['a'], dealerHand: ['9♦', '9♣'], // 18
      hands: { a: ['A♠', 'K♥'] }, bets: { a: 2 }, stood: { a: true }, bust: {},
      handKeys: { a: ['a'] }, fromSplit: {}, insurance: {},
    };
    const normal = bjResultFor(base, 'a');
    const afterSplit = bjResultFor({ ...base, fromSplit: { a: true } }, 'a');
    return { normal, afterSplit };
  });
  ok(bj21.normal.delta === 3, 'sima Blackjack 3:2-t fizet (2 tét → +3)', String(bj21.normal.delta));
  ok(bj21.afterSplit.delta === 2, 'split után ugyanaz a 21 csak 1:1', String(bj21.afterSplit.delta));

  // ── 6. biztosítás összege és kifizetése ──
  console.log('\n===== 6. BIZTOSÍTÁS =====');
  const ins = await p.evaluate(() => {
    const mk = (bet, chips) => ({ bets: { a: bet }, chips: { a: chips } });
    const amt = {
      bet1: bjInsuranceAmount(mk(1, 10), 'a'),
      bet2: bjInsuranceAmount(mk(2, 10), 'a'),
      bet3: bjInsuranceAmount(mk(3, 10), 'a'),
      bet5: bjInsuranceAmount(mk(5, 10), 'a'),
      tight: bjInsuranceAmount(mk(4, 5), 'a'),   // 5-4 = 1 fer bele
      none:  bjInsuranceAmount(mk(4, 4), 'a'),   // nincs mibol
    };
    const dealerBJ = { dealerHand: ['A♠', 'K♥'], insurance: { a: 2 } };
    const dealerNo = { dealerHand: ['A♠', '9♥'], insurance: { a: 2 } };
    return { amt, win: bjInsuranceResult(dealerBJ, 'a'), lose: bjInsuranceResult(dealerNo, 'a'),
             nothing: bjInsuranceResult({ dealerHand: ['A♠','K♥'], insurance: {} }, 'a') };
  });
  ok(ins.amt.bet1 === 1, '1-es tétnél 1 (a döntés szerint 1-re kerekítve)', String(ins.amt.bet1));
  ok(ins.amt.bet2 === 1, '2-es tétnél 1', String(ins.amt.bet2));
  ok(ins.amt.bet3 === 2, '3-as tétnél 2', String(ins.amt.bet3));
  ok(ins.amt.bet5 === 3, '5-ös tétnél 3', String(ins.amt.bet5));
  ok(ins.amt.tight === 1, 'csak annyi, amennyi a fő téten felül megvan', String(ins.amt.tight));
  ok(ins.amt.none === 0, 'ha nincs szabad zseton, nem biztosíthat', String(ins.amt.none));
  ok(ins.win.delta === 4, 'osztó-Blackjacknél 2:1 (2 → +4)', String(ins.win.delta));
  ok(ins.lose.delta === -2, 'egyébként elúszik', String(ins.lose.delta));
  ok(ins.nothing.delta === 0, 'aki nem biztosított, nem is veszít rajta', String(ins.nothing.delta));

  // ── 7. mikor indul a biztosítás-fázis ──
  console.log('\n===== 7. A BIZTOSÍTÁS-FÁZIS =====');
  const phases = await p.evaluate(() => {
    // Elore rakott pakli: bjPop a VEGEROL vesz, ezert forditva toltjuk.
    const mkDeck = (order) => [...order].reverse();
    const deal = (dealerUp, allowIns) => {
      const st = { participants: ['a'], bets: { a: 2 }, chips: { a: 10 }, stood: {}, bust: {}, doubled: {},
        allowIns, deck: mkDeck(['5♠', dealerUp, '6♥', '9♣', '2♦', '3♦', '4♦', '7♦']) };
      return bjDeal(st);
    };
    const withAce = deal('A♦', true);
    const withAceOff = deal('A♦', false);
    const withSix = deal('6♦', true);
    const dealerHasBJ = bjAfterInsurance({ ...withAce, dealerHand: ['A♦', 'K♣'], stood: {}, bust: {} });
    const dealerNoBJ = bjAfterInsurance({ ...withAce, dealerHand: ['A♦', '9♣'], stood: {}, bust: {} });
    return { withAce: withAce.phase, withAceOff: withAceOff.phase, withSix: withSix.phase,
             up: withAce.dealerHand[0], hasBJ: dealerHasBJ.phase, noBJ: dealerNoBJ.phase,
             keys: withAce.handKeys };
  });
  ok(phases.up === 'A♦', 'a teszt tényleg Ászt tett az osztó elé', phases.up);
  ok(phases.withAce === 'insurance', 'osztó-Ásznál biztosítás-fázis', phases.withAce);
  ok(phases.withAceOff === 'playing', 'kikapcsolva nincs biztosítás-fázis', phases.withAceOff);
  ok(phases.withSix === 'playing', 'nem-Ász felső lapnál sincs', phases.withSix);
  ok(phases.hasBJ === 'dealer', 'ha az osztónak Blackjackje van, a kör azonnal véget ér', phases.hasBJ);
  ok(phases.noBJ === 'playing', 'ha nincs, jöhet a játék', phases.noBJ);
  ok(JSON.stringify(phases.keys) === JSON.stringify({ a: ['a'] }), 'a leosztás felveszi a kéz-kulcsokat', JSON.stringify(phases.keys));

  // ── 8. a kör-egyenleg összegez ──
  console.log('\n===== 8. KÖR-EGYENLEG =====');
  const delta = await p.evaluate(() => {
    const st = {
      participants: ['a'], dealerHand: ['A♠', 'K♥'],           // oszto Blackjack
      hands: { a: ['8♠', '3♦'], 'a#1': ['8♥', '9♦'] },
      bets: { a: 2, 'a#1': 2 }, stood: { a: true, 'a#1': true }, bust: {},
      handKeys: { a: ['a', 'a#1'] }, fromSplit: { a: true, 'a#1': true },
      insurance: { a: 1 },
    };
    return { total: bjPlayerDelta(st, 'a'),
             hands: bjHandsOf(st, 'a').map(k => bjResultFor(st, k).delta),
             ins: bjInsuranceResult(st, 'a').delta };
  });
  ok(JSON.stringify(delta.hands) === JSON.stringify([-2, -2]), 'osztó-BJ mindkét kezet viszi', JSON.stringify(delta.hands));
  ok(delta.ins === 2, 'a biztosítás 2:1-et fizet', String(delta.ins));
  ok(delta.total === -2, 'a kör-egyenleg −2 (−2 −2 +2)', String(delta.total));

  // ── 9. régi, split nélküli állapot ──
  console.log('\n===== 9. RÉGI ÁLLAPOT VÁLTOZATLANUL =====');
  const legacy = await p.evaluate(() => {
    const old = { participants: ['a', 'b'], hands: { a: ['A♠','K♥'], b: ['9♠','8♥'] },
      bets: { a: 1, b: 1 }, stood: {}, bust: {}, dealerHand: ['7♦','9♣'] };
    return { keysA: bjHandsOf(old, 'a'), all: bjAllHandKeys(old),
             bjA: bjIsHandBJ(old, 'a'), resA: bjResultFor(old, 'a').delta,
             deltaA: bjPlayerDelta(old, 'a') };
  });
  ok(JSON.stringify(legacy.keysA) === JSON.stringify(['a']), 'handKeys nélkül a pid az egyetlen kéz', legacy.keysA.join(','));
  ok(JSON.stringify(legacy.all) === JSON.stringify(['a', 'b']), 'a kör-sorrend is stimmel', legacy.all.join(','));
  ok(legacy.bjA === true, 'a Blackjack Blackjack marad');
  ok(legacy.resA === 2 && legacy.deltaA === 2, 'a kifizetés változatlan', `${legacy.resA} / ${legacy.deltaA}`);

  // ── 10. telefonos felület ──
  console.log('\n===== 10. TELEFONOS FELÜLET =====');
  const mkRoom = (bjState) => ({
    players: [{ id:'a', name:'Alfa', color:'#E07A5F' }, { id:'b', name:'Beta', color:'#4FC2A0' }],
    bjTakenIds: ['a'], bjState,
  });
  const render = async (bjState) => {
    await p.evaluate((room) => {
      const old = document.getElementById('__p'); if (old) old.remove();
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__p';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;overflow:auto';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(BlackjackObserverView, {
        room, code: '123456', onLeave: () => {}, initialPlayerId: 'a', onPlayerIdChange: () => {},
      }));
    }, mkRoom(bjState));
    await p.waitForTimeout(900);
    return p.evaluate(() => document.querySelector('#__p').innerText.replace(/\s+/g, ' '));
  };

  const insTxt = await render({
    phase:'insurance', gameIdx:0, participants:['a','b'], deck:[],
    hands:{ a:['9♠','7♥'], b:['5♠','6♥'] }, dealerHand:['A♦','K♣'],
    bets:{ a:4, b:1 }, chips:{ a:10, b:10 }, stood:{}, bust:{}, doubled:{},
    handKeys:{ a:['a'], b:['b'] }, fromSplit:{}, aceSplit:{}, insurance:{}, insDone:{},
    startStack:10, stacks:{}, cashedOut:{}, allowIns:true, allowSplit:true, currentTurn:null,
  });
  ok(/Ászt mutat/.test(insTxt), 'a telefon felajánlja a biztosítást', insTxt.slice(0, 90));
  ok(/Kérek \(2\)/.test(insTxt), '4-es tétnél 2 zsetont ajánl', (insTxt.match(/Kérek \(\d+\)/) || ['—'])[0]);

  const splitTxt = await render({
    phase:'playing', gameIdx:0, participants:['a','b'], deck:['2♣','3♣'],
    hands:{ a:['8♠','3♦'], 'a#1':['8♥','9♦'], b:['5♠','6♥'] }, dealerHand:['6♦','9♣'],
    bets:{ a:2, 'a#1':2, b:1 }, chips:{ a:10, b:10 }, stood:{}, bust:{}, doubled:{},
    handKeys:{ a:['a','a#1'], b:['b'] }, fromSplit:{ a:true, 'a#1':true }, aceSplit:{},
    insurance:{}, insDone:{}, startStack:10, stacks:{}, cashedOut:{},
    allowIns:true, allowSplit:true, currentTurn:'a',
  });
  // A felirat CSUPA NAGYBETŰS a stílus miatt, az innerText ezt így adja vissza
  ok(/A KEZEID/i.test(splitTxt), 'a telefon "A kezeid"-et ír két kéznél',
     (splitTxt.match(/A (KEZEID|LAPJAID)/i) || ['—'])[0]);
  ok(/1\. KÉZ · TÉT 2/.test(splitTxt) && /2\. KÉZ · TÉT 2/.test(splitTxt),
     'mindkét kéz látszik a saját tétjével', (splitTxt.match(/\d\. KÉZ · TÉT \d/g) || []).join(' | '));
  ok(/TE JÖSSZ/.test(splitTxt), 'a soros kéz nálam van, tehát én jövök');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
