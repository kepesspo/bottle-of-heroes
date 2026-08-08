// v10.325 — Blackjack telefonos felület: a küldött mockupok szerinti elrendezés
//
// Három képernyő, három állítás — mind olyan, ami a RÉGI változaton bukik:
//   1. Csatlakozás: a három készlet-csempe EGY SORBAN áll (eddig egymás alatt,
//      teljes szélességű gombként), és a kijelölt borostyán keretet visz.
//   2. Tét: van gyorsválasztó sor (1/2/3/5 korty), és ami nem fér a készletbe,
//      az LE VAN TILTVA — különben egy koppintással olyan tétet állítana be,
//      amit a `setMyBet` clamp-je úgyis visszavág, és a felület mást mutatna,
//      mint ami tényleg bemegy.
//   3. Asztal: az akciógombok KÖRÖK, a felirat a kör ALATT (nem a feliratban
//      álló emoji), egy kéznél a pontszám a fejléc sorában van, és a helyeket
//      függőleges vonal választja el (nem csempe-háttér).
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'p0', name:'Tóth', color:'#6FA86F' },
            { id:'p1', name:'Márk', color:'#4C8DD8' },
            { id:'p2', name:'Kecsi', color:'#7BA05B' }];

const base = { stacks:{ p0:10 }, startStack:10, stood:{}, bust:{}, doubled:{}, handKeys:{}, hands:{}, dealerHand:[], bets:{}, betsDone:{}, chips:{} };
const SCENES = {
  joining: { ...base, phase:'joining', participants:[] },
  // keszlet 3 → az „5 korty" gyorsvalaszto nem fer bele
  betting: { ...base, phase:'betting', participants:['p0','p1'], chips:{ p0:3, p1:10 }, bets:{ p0:1, p1:1 } },
  playing: { ...base, phase:'playing', participants:['p0','p1','p2'], chips:{ p0:20, p1:20, p2:20 },
             bets:{ p0:5, p1:5, p2:5 }, betsDone:{ p0:true, p1:true, p2:true },
             hands:{ p0:['2♦','Q♠'], p1:['7♣','9♥'], p2:['A♠','3♦'] }, dealerHand:['5♠','K♦'],
             handKeys:{ p0:['p0'], p1:['p1'], p2:['p2'] }, currentTurn:'p0', allowSplit:true, allowDouble:true },
};

async function mount(b, bjState) {
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  await p.evaluate(({ pl, bjState }) => {
    window.__fbStore['rooms'] = { '801118': { players: pl, bjTakenIds: ['p0'], bjState } };
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(BlackjackObserverView, {
      room: { players: pl, bjTakenIds: ['p0'], bjState }, code:'801118', onLeave:()=>{},
      keepClaimOnUnmount: true, initialPlayerId:'p0', onPlayerIdChange:()=>{}, onSwitchToHost:()=>{},
    }));
  }, { pl: PL, bjState });
  await p.waitForTimeout(1500);
  return p;
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. csatlakozás ──
  console.log('\n===== 1. CSATLAKOZAS =====');
  let p = await mount(b, SCENES.joining);
  const tiles = await p.evaluate(() => [...document.querySelectorAll('#__p button')]
    .filter(x => /KORTY/i.test(x.innerText || ''))
    .map(x => { const r = x.getBoundingClientRect(); const cs = getComputedStyle(x);
                return { t:Math.round(r.top), l:Math.round(r.left), w:Math.round(r.width),
                         txt:(x.innerText||'').replace(/\s+/g,' ').trim(), pressed:x.getAttribute('aria-pressed'),
                         border:cs.borderTopColor }; }));
  ok(tiles.length === 3, 'harom keszlet-csempe', tiles.length);
  ok(tiles.length === 3 && new Set(tiles.map(x => x.t)).size === 1,
     'EGY SORBAN allnak (azonos felso el)', JSON.stringify(tiles.map(x => x.t)));
  ok(tiles.length === 3 && new Set(tiles.map(x => x.l)).size === 3,
     'harom kulonbozo vizszintes pozicio (nem egymas alatt)', JSON.stringify(tiles.map(x => x.l)));
  ok(tiles.every(x => x.w < 200), 'egyik sem teljes szelessegu', JSON.stringify(tiles.map(x => x.w)));
  ok(tiles.map(x => x.txt.replace(/[^0-9]/g,'')).join(',') === '5,10,20', 'a harom ertek 5 / 10 / 20',
     tiles.map(x => x.txt).join(' | '));
  const selT = tiles.filter(x => x.pressed === 'true');
  ok(selT.length === 1 && /10/.test(selT[0].txt), 'pontosan egy van kijelolve (a 10)', JSON.stringify(selT.map(x=>x.txt)));
  // borostyan keret a kijeloltnel — a tobbi atlatszo
  ok(selT.length === 1 && !/rgba\(0, 0, 0, 0\)/.test(selT[0].border),
     'a kijelolt csempenek lathato (borostyan) kerete van', selT.length ? selT[0].border : '-');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 2. tét ──
  console.log('\n===== 2. TET =====');
  p = await mount(b, SCENES.betting);
  const quick = await p.evaluate(() => [...document.querySelectorAll('#__p button')]
    .filter(x => /^\d+ korty$/.test((x.innerText || '').replace(/\s+/g,' ').trim()))
    .map(x => ({ txt:(x.innerText||'').replace(/\s+/g,' ').trim(), off:x.disabled, top:Math.round(x.getBoundingClientRect().top) })));
  ok(quick.length === 4, 'negy gyorsvalaszto', quick.map(x=>x.txt).join(','));
  ok(new Set(quick.map(x => x.top)).size === 1, 'egy sorban allnak', JSON.stringify(quick.map(x=>x.top)));
  // keszlet = 3 → az 5-os nem fer bele
  ok(quick.filter(x => x.off).map(x => x.txt).join(',') === '5 korty',
     'a keszletnel nagyobb tet LE VAN TILTVA (keszlet: 3)', JSON.stringify(quick.map(x => x.txt + (x.off?' [tiltva]':''))));
  const steppers = await p.evaluate(() => ['Egy korttyal kevesebb','Egy korttyal több'].map(l => {
    const x = document.querySelector(`#__p button[aria-label="${l}"]`);
    if (!x) return null;
    const cs = getComputedStyle(x), r = x.getBoundingClientRect();
    return { round: cs.borderTopLeftRadius === '50%' || parseFloat(cs.borderTopLeftRadius) >= r.width/2 - 1,
             w:Math.round(r.width), h:Math.round(r.height) };
  }));
  ok(steppers.every(x => x && x.round), 'a −/+ leptetok KOROK', JSON.stringify(steppers));
  ok(steppers.every(x => x && x.w === x.h), 'negyzetes befoglalo (tehat szabalyos kor)', JSON.stringify(steppers));
  ok(await p.evaluate(() => [...document.querySelectorAll('#__p button')].some(x => /Tét megerősítése/.test(x.innerText||''))),
     'megvan a „Tét megerősítése" gomb');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 3. asztal ──
  console.log('\n===== 3. ASZTAL =====');
  p = await mount(b, SCENES.playing);
  const acts = await p.evaluate(() => ['Hit','Stand','Dupla'].map(l => {
    const x = document.querySelector(`#__p button[aria-label="${l}"]`);
    if (!x) return null;
    const disc = x.firstElementChild, lbl = x.lastElementChild;
    if (!disc || !lbl) return { label:l, bad:'nincs ket resz' };
    const dr = disc.getBoundingClientRect(), lr = lbl.getBoundingClientRect();
    return { label:l, txt:(lbl.textContent||'').trim(),
             round: getComputedStyle(disc).borderTopLeftRadius === '50%',
             below: lr.top >= dr.bottom - 1, w:Math.round(dr.width), h:Math.round(dr.height) };
  }));
  ok(acts.every(Boolean), 'megvan mind a harom akciogomb (Hit / Stand / Dupla)', JSON.stringify(acts.map(a=>a&&a.label)));
  ok(acts.every(a => a && a.round), 'a korong KOR alaku', JSON.stringify(acts.map(a=>a&&a.round)));
  ok(acts.every(a => a && a.w === a.h && a.w >= 60), 'a korong szabalyos es eleg nagy', JSON.stringify(acts.map(a=>a&&a.w)));
  ok(acts.every(a => a && a.below), 'a felirat a korong ALATT all', JSON.stringify(acts.map(a=>a&&a.below)));
  ok(acts.map(a => a && a.txt).join(',') === 'Hit,Stand,Dupla', 'a feliratok szovegesek, emoji nelkul',
     acts.map(a=>a&&a.txt).join(','));

  // egy keznel a pontszam a fejlec soraban
  const hdr = await p.evaluate(() => {
    const lbl = [...document.querySelectorAll('#__p span')].find(x => (x.textContent||'').trim() === 'A lapjaid');
    if (!lbl) return null;
    const row = lbl.parentElement;
    const sc = [...row.children].find(x => /^\d+$/.test((x.textContent||'').trim()));
    return { inRow: !!sc, score: sc ? sc.textContent.trim() : null, kids: row.children.length };
  });
  ok(hdr && hdr.inRow, 'egy keznel a pontszam a fejlec SORABAN van', hdr && hdr.score);
  ok(hdr && hdr.score === '12', 'a pontszam helyes (2♦ + Q♠ = 12)', hdr && hdr.score);

  // helyek: nincs csempe-hatter, van fuggoleges elvalaszto
  const seats = await p.evaluate(() => {
    const names = ['Márk','Kecsi'].map(n => [...document.querySelectorAll('#__p span')]
      .find(x => (x.textContent||'').trim() === n));
    if (names.some(x => !x)) return null;
    const boxes = names.map(x => x.parentElement);
    const parent = boxes[0].parentElement;
    const seps = [...parent.children].filter(c => {
      const r = c.getBoundingClientRect();
      return r.width <= 2 && r.height > 20;
    });
    return { tops: boxes.map(x => Math.round(x.getBoundingClientRect().top)),
             bgs: boxes.map(x => getComputedStyle(x).backgroundColor),
             seps: seps.length };
  });
  ok(seats && new Set(seats.tops).size === 1, 'a ket hely egy sorban', seats && JSON.stringify(seats.tops));
  ok(seats && seats.bgs.every(c => /rgba\(0, 0, 0, 0\)/.test(c)),
     'a helynek NINCS sajat csempe-hattere', seats && JSON.stringify(seats.bgs));
  ok(seats && seats.seps === 1, 'pontosan egy fuggoleges elvalaszto a ket hely kozott', seats && seats.seps);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
