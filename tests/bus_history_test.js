// v10.324 — Busz: a megállóra koppintva látszik, mi fordult ott KORÁBBAN
//
// A „Húzott lapok" sor pozíciónként mindig csak az UTOLSÓ lapot mutatja
// (`busPositionDrawnCards`), mert a következő buszozó felülírja. Az előzményt
// ezért külön térkép őrzi (`busPositionHistory`), és a megállóra koppintva
// nyílik meg.
//
// Amit ellenőriz:
//   1. a helyer (`busPushHistory`) hozzáfűz, több buszozót is elbír egy húzáson,
//      és a plafonnál a LEGRÉGEBBIT dobja el (nem a legújabbat)
//   2. a valódi játékmenet tényleg tölti a térképet — három bukott tipp
//      ugyanazon a megállón három bejegyzést ad, miközben a „Húzott lapok"
//      sorban továbbra is csak az utolsó lap áll
//   3. a jelvény a darabszámot mutatja, és a lapon mind a három ott van,
//      a bukást jelölve
//
// A 2. blokk a lényeg: seedelt előzménnyel a renderelés akkor is átmenne, ha
// a könyvelés soha nem írna semmit.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PLAYERS = [{ id:'p0', name:'Sere', color:'#E0655F' },
                 { id:'p1', name:'Luca', color:'#A78BFA' },
                 { id:'p2', name:'Dani', color:'#4FC2A0' }];

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 920 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // ── 1. a helyer ──
  console.log('\n===== 1. A HELYER =====');
  const h = await p.evaluate(() => {
    const C = v => ({ suit:'♠', value:v });
    let m = busPushHistory({}, 2, C('5'), ['p0','p1'], { p0:{correct:true}, p1:{correct:false} });
    m = busPushHistory(m, 2, C('9'), ['p0'], { p0:{correct:false} });
    m = busPushHistory(m, 3, C('K'), ['p1'], { p1:{correct:true} });
    // plafon: 15 hozzafuzes 12-es limittel
    let big = {};
    for (let i = 0; i < 15; i++) big = busPushHistory(big, 0, C(String(i)), ['p0'], { p0:{correct:true} });
    return { two: m['2'], three: m['3'], bigLen: big['0'].length,
             bigFirst: big['0'][0].c.value, bigLast: big['0'][big['0'].length-1].c.value,
             max: BUS_HISTORY_MAX };
  });
  ok(h.two.length === 2, 'ugyanarra a megallora hozzafuz', h.two.length);
  ok(h.two[0].r.length === 2, 'EGY huzas TOBB buszozohoz is tartozhat', JSON.stringify(h.two[0].r));
  ok(h.two[0].r[0].ok === true && h.two[0].r[1].ok === false, 'buszozonkent kulon jegyzi a talalatot');
  ok(h.three.length === 1, 'a megallok kulon sorban allnak', h.three.length);
  ok(h.bigLen === h.max, 'a plafon tartja magat', h.bigLen + ' / ' + h.max);
  ok(h.bigFirst === '3' && h.bigLast === '14', 'a plafonnal a LEGREGEBBI esik ki, nem a legujabb',
     h.bigFirst + '…' + h.bigLast);

  // ── 2-3. valodi jatekmenet ──
  // p0 egyedul buszozik a 0. megallon (utvonal-lap ♥2). Minden huzott lap 2-nel
  // NAGYOBB, tehat a „Kisebb" mindig bukik → a jatekos a 0-n marad, es ugyanoda
  // kerul minden bejegyzes.
  console.log('\n===== 2. A JATEKMENET TOLTI =====');
  await p.evaluate((pl) => {
    window.__fbStore['rooms'] = { '424242': { players: pl, buszTakenIds: ['p0','p1','p2'],
      buszState: { phase:'bus', settings:{ deckCount:1, busSteps:6 },
        busRiders:['p0'], busRiderDone:{}, busWatchers:{},
        busRiderPositions:{ p0:0 }, busRiderDrawnCards:{ p0:[] },
        busRouteCards:[{suit:'♥',value:'2'},{suit:'♦',value:'7'},{suit:'♣',value:'9'},
                       {suit:'♠',value:'K'},{suit:'♥',value:'4'},{suit:'♦',value:'3'}],
        busDrawDeck:[{suit:'♣',value:'5'},{suit:'♠',value:'Q'},{suit:'♦',value:'6'},{suit:'♥',value:'8'}],
        busRevealedPositions:[1,3], currentTurnRiderId:'p0', busRiderPendingGuesses:{}, busRiderDrinks:{} } } };
  }, PLAYERS);
  await p.evaluate((pl) => {
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(BuszGame, {
      players: pl, roomCode:'424242', gameIdx:0, gameMeta:{ buszConfig:{ deckCount:1, busSteps:6 } },
      onAdvance:()=>{}, onSetHideFooter:()=>{}, onSetBuszSwitch:()=>{},
    }));
  }, PLAYERS);
  await p.waitForTimeout(2200);
  // „Ki vagy?" — a host Dani, aki NEM buszozik, igy a host tablat kapjuk
  await p.evaluate(() => { const x = [...document.querySelectorAll('#__p button')].find(y => /Dani/.test(y.innerText||'')); if (x) x.click(); });
  await p.waitForTimeout(500);
  await p.evaluate(() => { const x = [...document.querySelectorAll('#__p button')].find(y => /Válassz|Mehet|Ez vagyok/.test(y.innerText||'')); if (x) x.click(); });
  await p.waitForTimeout(1500);

  const st = () => p.evaluate(() => window.__fbStore['rooms']['424242'].buszState);
  // Bukas utan a host tablan 6 mp-ig all az eredmeny-sav (es a korty-overlay),
  // a tipp-gombok addig nem elnek. Ezert varunk a gombra, nem fix idot alszunk —
  // fix varakozassal a masodik es harmadik kattintas nemán elveszne.
  const guessLower = async () => {
    for (let k = 0; k < 40; k++) {
      const clicked = await p.evaluate(() => {
        const x = [...document.querySelectorAll('#__p button')].find(y => /Kisebb/.test(y.innerText || ''));
        if (!x) return false;
        const r = x.getBoundingClientRect();
        const top = document.elementFromPoint(Math.round(r.left + r.width/2), Math.round(r.top + r.height/2));
        if (!top || !x.contains(top)) return false;   // valami rafekszik
        x.click(); return true;
      });
      if (clicked) { await p.waitForTimeout(900); return true; }
      await p.waitForTimeout(400);
    }
    return false;
  };
  for (let i = 0; i < 3; i++) ok(await guessLower(), `${i+1}. tipp bement`);

  const s = await st();
  const hist0 = (s.busPositionHistory || {})['0'] || [];
  ok(hist0.length === 3, 'harom bukott tipp → harom bejegyzes a 0. megallon', hist0.length);
  ok(hist0.every(e => e.r.length === 1 && e.r[0].id === 'p0' && e.r[0].ok === false),
     'mindharom bukas p0-hoz van jegyezve', JSON.stringify(hist0.map(e => e.r)));
  const lastCard = (s.busPositionDrawnCards || {})['0'];
  ok(lastCard && lastCard.value === hist0[2].c.value,
     'a „Húzott lapok" sor az UTOLSO lapot mutatja', lastCard && lastCard.value);
  ok(new Set(hist0.map(e => e.c.value)).size === 3,
     'a harom bejegyzes harom KULONBOZO lap (nem az utolso haromszor)',
     hist0.map(e => e.c.value).join(','));

  // ── 3. a felulet ──
  console.log('\n===== 3. A MEGALLO-LAP =====');
  // A gomb szovege a LAPOT is tartalmazza (ertek + ket szin), a jelveny az
  // utolso gyermek — ezert nem az innerText-et olvassuk.
  const badge = await p.evaluate(() => {
    const btn = [...document.querySelectorAll('#__p button')].find(x => /1\. megálló előzménye/.test(x.getAttribute('aria-label') || ''));
    if (!btn) return null;
    const sp = btn.lastElementChild;
    return sp && sp.tagName === 'SPAN' ? (sp.textContent || '').trim() : 'NINCS JELVENY';
  });
  ok(badge === '3', 'a jelveny a darabszamot mutatja', JSON.stringify(badge));

  await p.evaluate(() => {
    const btn = [...document.querySelectorAll('#__p button')].find(x => /1\. megálló előzménye/.test(x.getAttribute('aria-label') || ''));
    if (btn) btn.click();
  });
  await p.waitForTimeout(900);
  const sheet = await p.evaluate(() => document.body.innerText);
  ok(/1\. megálló/.test(sheet), 'a lap cime a megallo sorszama');
  ok(/Eddig 3 lap fordult itt/.test(sheet), 'kiirja, hany lap fordult ott');
  ok((sheet.match(/Sere/g) || []).length >= 3, 'mind a harom sorban ott a buszozo neve',
     (sheet.match(/Sere/g) || []).length);
  ok(/A megálló lapja/.test(sheet), 'a megallo lapja is latszik (a bukas felfedte)');
  const rows = await p.evaluate(() => {
    const lbl = [...document.querySelectorAll('div')].find(x => x.children.length === 0 && (x.textContent || '').trim() === 'Ami itt fordult');
    return lbl && lbl.nextElementSibling ? lbl.nextElementSibling.children.length : -1;
  });
  ok(rows === 3, 'harom sor all a lapon', rows);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.screenshot({ path: ROOT + '/tests/bus_history_sheet.png' });
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
