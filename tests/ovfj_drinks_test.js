// v10.359 — Ország-Város: a kortyok VÉGRE felkerülnek, plafonnal
//
// ⚠️ AZ EREDETI HIBA MÉRVE VOLT, nem feltételezve: a kör végi banner
// „Alfa: 3 korty"-ot írt, `drinks: 3`-mal — a játék viszont EGYETLEN könyvelő
// hívást sem küldött. Se `onAdvance` valódi térképpel, se `onLiveDrinkUpdate`;
// a `onAdvance({})` egyszer futott, a legvégén, ÜRESEN. Vagyis a kortyok soha
// nem kerültek fel a `players[].drinks` mezőre, tehát a parti végi
// statisztikába sem — miközben a banner végig azt mondta, hogy valaki iszik.
//
// ⚠️ EZÉRT A FOGÓDZÓ A JÁTÉKOS-ÁLLAPOT, nem a banner. A banner a hibás
// verzión is helyesen írta ki a számot — pont ez tette láthatatlanná.
//
// A plafon (`OVFJ_MAX_DRINKS = 5`) tulajdonosi döntés: a játék a TELJES
// pontkülönbséget osztaná ki kortyban, ami több válasznál egy körben húsz is
// lehetne. Amíg semmi nem került fel, ez nem látszott.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const CATS = ['orszag','varos','fiu','lany','noveny','allat','targy','hires'];

const click = (p, re) => p.evaluate(r => {
  const rx = new RegExp(r);
  const b = [...document.querySelectorAll('button')].find(x => rx.test((x.innerText || '').replace(/\s+/g, ' ')));
  if (b) { b.click(); return true; } return false;
}, re.source);

const txt = p => p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
const players = p => p.evaluate(() => (window.__players || []).map(x => ({ n:x.name, dr:x.drinks })));

// Egy teljes kort visz vegig: a host (Alfa) SEMMIT nem ir, a telefonos Beta
// pedig `nCats` kategoriat tolt ki — igy a pontkulonbseg pontosan `nCats`.
async function playRound(b, { difficulty, nCats }) {
  const p = await b.newPage({ viewport: { width: 402, height: 1200 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}
    window.__diff = ${JSON.stringify(difficulty)};`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);
  await p.evaluate(() => {
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto;padding:12px;box-sizing:border-box';
    document.body.appendChild(root);
    const PL = [{ id:'a', name:'Alfa', color:'#E07A5F', points:0, drinks:0 },
                { id:'b', name:'Beta', color:'#4FC2A0', points:0, drinks:0 }];
    function H() {
      const [ps, setPs] = React.useState(PL);
      window.__players = ps;
      return React.createElement(PlayScreen, { go:()=>{}, players:ps, setPlayers:setPs,
        selectedGames:['ovfj'], roomCode:'123456',
        gameMeta:{ modes:['points'], difficulty: window.__diff, ovfjConfig:{ rounds:3, roundTime:90 } },
        setGameMeta:()=>{}, setScoreHistory:()=>{}, setLastGameRound:()=>{} });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(1600);
  await p.evaluate(() => firebase.firestore().collection('rooms').doc('123456')
    .set({ ovfjTakenIds: ['b'] }, { merge: true }));
  await click(p, /Alfa/);      await p.waitForTimeout(500);
  await click(p, /Én vagyok/); await p.waitForTimeout(900);
  await click(p, /Kezdés/);    await p.waitForTimeout(5200);   // 4 mp betűsorsolás

  // Beta bekuldi a szavakat — a HUZOTT betuvel, kulonben ervenytelenek.
  await p.evaluate(async ({ cats, n }) => {
    const st = window.__fbStore['rooms']['123456'].ovfjState;
    const L = (st.letter || 'A').charAt(0);
    const rec = { pid:'b', sess: st.sess, round: st.round, done:true, doneAt: Date.now() };
    cats.slice(0, n).forEach((c, i) => { rec[c] = L + 'szó' + i; });
    await firebase.firestore().collection('rooms').doc('123456')
      .set({ ovfjA_b: rec }, { merge: true });
  }, { cats: CATS, n: nCats });
  await p.waitForTimeout(700);
  await click(p, /Kész vagyok/); await p.waitForTimeout(1200);
  await click(p, /Befejezés/);   await p.waitForTimeout(1800);
  return p;
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. A KORTYOK FELKERULNEK ──
  // ⚠️ A hibas verzion ez a blokk bukik: a banner ugyanezt irta, de a
  // `players[].drinks` VEGIG 0 maradt.
  console.log('\n===== 1. A KORTYOK FELKERULNEK =====');
  {
    const p = await playRound(b, { difficulty: 'easy', nCats: 3 });
    const t = await txt(p);
    ok(/kör vége/.test(t), 'eljutottunk a kör végi képernyőre', t.slice(0, 60));
    const st = await players(p);
    ok(st[0].dr === 3, 'a lemaradó játékosra felkerült a 3 korty', JSON.stringify(st));
    ok(st[1].dr === 0, 'a vezető nem iszik', JSON.stringify(st));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 2. A PLAFON ──
  // Nyolc kategoria -> 8 pont kulonbseg, de a plafon 5.
  console.log('\n===== 2. A PLAFON (max 5) =====');
  {
    const p = await playRound(b, { difficulty: 'easy', nCats: 8 });
    const st = await players(p);
    ok(st[0].dr === 5, '8 pont különbségnél is legfeljebb 5 korty', JSON.stringify(st));
    // a banner szamanak UGYANAZT kell mondania
    ok(/Alfa: 5 korty/.test(await txt(p)), 'és a banner is 5-öt ír',
       ((await txt(p)).match(/Alfa: \d+ korty/) || ['—'])[0]);
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 3. A NEHEZSEG SZOROZ, es a HAROM szam egyezik ──
  // ⚠️ Harom helyen kell ugyanannak lennie: a konyveles (`onLiveDrinkUpdate`,
  // ami NEM szoroz), a banner szama (`onResult`, ami MAGA szoroz), es a
  // felirat kezi szamai. Barmelyik kimaradasa nema ellentmondast adna.
  console.log('\n===== 3. A NEHEZSEG SZORZOJA =====');
  {
    const p = await playRound(b, { difficulty: 'hard', nCats: 3 });   // ×3
    const st = await players(p);
    ok(st[0].dr === 9, 'nehéz szinten a 3 pont különbség 9 korty', JSON.stringify(st));
    ok(/Alfa: 9 korty/.test(await txt(p)), 'és a banner felirata is 9-et ír',
       ((await txt(p)).match(/Alfa: \d+ korty/) || ['—'])[0]);
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 4. DONTETLEN: senki nem iszik ──
  console.log('\n===== 4. DONTETLEN =====');
  {
    const p = await playRound(b, { difficulty: 'easy', nCats: 0 });
    const st = await players(p);
    ok(st.every(x => x.dr === 0), 'ha senki nem írt semmit, senki nem iszik', JSON.stringify(st));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
