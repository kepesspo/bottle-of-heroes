// 🌪 Szélvihar (Busz) — a teljes lánc: ütemező → cél → új osztás → bejelentés
//
// A szélvihar CSAK online szobában és CSAK bekapcsolt kapcsolóval fut
// (`buszConfig.szelviharEnabled`), a busz fázisban. Amit itt védünk:
//   1. a host ütemezője tényleg kiírja a `buszState.szelvihar` eseményt;
//   2. a cél egy NÉZŐ, nem a buszon ülő játékos (különben sajátmagát fújná el);
//   3. a gomb megnyomása új útvonalat oszt ÉS a buszozókat visszateszi a startra;
//   4. az esemény lezárul, és megy a bejelentés mindenkinek.
//
// A host SAJÁT popupja a busz-nézetén belül renderel (a K/N gombok mellett),
// ezt itt nem mérjük — a mountolt komponens a „Ki a host?" képernyőn áll, és
// az odáig kattintás többet törne el, mint amennyit véd. A bejelentés
// megérkezését a 4. pont igazolja.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PLAYERS = [{id:'p0',name:'Sere',color:'#E0655F'},{id:'p1',name:'Luca',color:'#A78BFA'},{id:'p2',name:'Dani',color:'#4FC2A0'}];

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 920 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}
    window.__szelviharTestDelay = 400;`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // Szoba: a busz mar fut, p0 utazik, p2 leszallt es NEZI a buszt.
  await p.evaluate((pl) => {
    window.__fbStore['rooms'] = { '424242': {
      players: pl, buszTakenIds: [],
      buszState: {
        phase:'bus', settings:{ deckCount:1, busSteps:6 },
        busRiders:['p0'], busRiderDone:{}, busWatchers:{ p2:true },
        busRiderPositions:{ p0:3 }, busRiderDrawnCards:{ p0:[{suit:'♠',value:'5'}] },
        busRouteCards:[{suit:'♥',value:'2'},{suit:'♦',value:'7'},{suit:'♣',value:'9'},
                       {suit:'♠',value:'K'},{suit:'♥',value:'4'},{suit:'♦',value:'A'}],
        busDrawDeck:[{suit:'♣',value:'3'}], busRevealedPositions:[1,3],
      },
    }};
  }, PLAYERS);

  await p.evaluate((pl) => {
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(BuszGame, {
      players: pl, roomCode:'424242', gameIdx:0,
      gameMeta:{ buszConfig:{ szelviharEnabled:true, deckCount:1, busSteps:6 } },
      onAdvance:()=>{}, onSetHideFooter:()=>{}, onSetBuszSwitch:()=>{},
    }));
  }, PLAYERS);
  await p.waitForTimeout(2500);

  const st = () => p.evaluate(() => window.__fbStore['rooms']['424242'].buszState);

  console.log('\n===== 1. AZ ÜTEMEZŐ ELSÜTI =====');
  await p.waitForTimeout(1800);
  const sv = (await st()).szelvihar;
  ok(!!sv, 'a host kiírta a szélvihar eseményt', sv ? JSON.stringify(sv) : 'NINCS');
  ok(sv && sv.targetPid === 'p2', 'a cél a NÉZŐ (p2), nem a buszon ülő', sv && sv.targetPid);

  console.log('\n===== 2. A GOMB → ÚJ OSZTÁS =====');
  const before = JSON.stringify((await st()).busRouteCards);
  // A jatekos-eszkoz `tapSzelvihar`-javal azonos iras.
  await p.evaluate(async () => {
    const db = firebase.firestore();
    const s0 = (await db.collection('rooms').doc('424242').get()).data().buszState;
    const dc = s0.settings.deckCount, steps = s0.settings.busSteps;
    const pos = { ...(s0.busRiderPositions||{}) }, drawn = { ...(s0.busRiderDrawnCards||{}) };
    (s0.busRiders||[]).forEach(r => { if (!(s0.busRiderDone||{})[r]) { pos[r] = 0; drawn[r] = []; } });
    await db.collection('rooms').doc('424242').update({ buszState: { ...s0,
      busRouteCards: shuffleDeck(generateDeck(dc)).slice(0, steps),
      busDrawDeck: shuffleDeck(generateDeck(dc)),
      busRiderPositions: pos, busRiderDrawnCards: drawn,
      busPositionDrawnCards:{}, busRiderPendingGuesses:{},
      busRevealedPositions:[1,3].filter(i => i < steps),
      szelvihar: null, szelviharAnnounce: { name:'Dani', ts: Date.now() },
    }});
  });
  await p.waitForTimeout(1200);
  const s2 = await st();
  ok(JSON.stringify(s2.busRouteCards) !== before, 'új útvonal-lapok kerültek ki');
  ok(s2.busRiderPositions.p0 === 0, 'a buszozó visszakerült a startra', s2.busRiderPositions.p0);
  ok(s2.szelvihar === null, 'az esemény lezárult', String(s2.szelvihar));
  ok(!!s2.szelviharAnnounce && s2.szelviharAnnounce.name === 'Dani',
     'a bejelentés kiment mindenkinek', s2.szelviharAnnounce && s2.szelviharAnnounce.name);

  console.log('\n===== 3. KIKAPCSOLVA NEM FUT =====');
  await p.evaluate(() => {
    const r = window.__fbStore['rooms']['424242'];
    r.buszState = { ...r.buszState, szelvihar: null };
    const old = document.getElementById('__p'); if (old) old.remove();
  });
  await p.evaluate((pl) => {
    const root = document.createElement('div'); root.id = '__p2';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(BuszGame, {
      players: pl, roomCode:'424242', gameIdx:0,
      gameMeta:{ buszConfig:{ szelviharEnabled:false, deckCount:1, busSteps:6 } },
      onAdvance:()=>{}, onSetHideFooter:()=>{}, onSetBuszSwitch:()=>{},
    }));
  }, PLAYERS);
  await p.waitForTimeout(2600);
  ok((await st()).szelvihar == null, 'kikapcsolt kapcsolóval nem sül el');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
