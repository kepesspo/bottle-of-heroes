// v10.377 — Beer Pong 2.0: telefonos eredmény-beküldés
//
// A meccs játékosai a telefonjukon állítják a poharat és BEKÜLDIK; a host marad
// a hiteles, EGY koppintással elfogadja. A csatorna a szoba `bp2Submit` mezője
// (nem a bp2State — az a hoste). A javaslat a két játékos id-jére hivatkozik,
// így egy elavult meccsre szóló beküldést a render kiszűr.
//
// Fogódzók:
//  1) a telefon a jelenlegi meccshez „Eredmény beküldése" panelt mutat
//  2) beküldés → a szoba bp2Submit mezője megtelik
//  3) a HOST-on megjelenik a jóváhagyó sáv a beküldött eredménnyel
//  4) „Elfogadom" → a meccs rögzül (2 főnél = bajnok), a bajnok pontot kap,
//     és a bp2Submit törlődik
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990011';

const store = p => p.evaluate(c => window.__fbStore['rooms'][c] || {}, CODE);
const hostTxt = p => p.evaluate(() => (document.getElementById('__host').innerText || '').replace(/\s+/g, ' '));
const phoneTxt = p => p.evaluate(() => (document.getElementById('__phone').innerText || '').replace(/\s+/g, ' '));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1600 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // HOST (nagy képernyő) + TELEFON (observer), EGY szobán
  await p.evaluate(({ code }) => {
    const pl = [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 }];
    window.__fbStore['rooms'] = { [code]: { code, players: pl, gameIdx: 0, selectedGames: ['beerpong2'] } };
    window.__adv = null;
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:820px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      gameMeta: { beerpong2Config: { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:0 } },
      onAdvance: (dm, pm) => { window.__adv = { dm, pm }; }, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
    // TELEFON — a szoba pillanatképét figyeli
    const f = document.createElement('div'); f.id = '__phone';
    f.style.cssText = 'position:absolute;left:0;top:840px;width:402px;height:740px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(f);
    function W() {
      const [room, setRoom] = React.useState(() => window.__fbStore['rooms'][code]);
      React.useEffect(() => firebase.firestore().collection('rooms').doc(code).onSnapshot(s => setRoom(s.data() || null)), []);
      if (!room) return null;
      return React.createElement(BeerPong2ObserverView, { room, code, observerName: 'Sere', onLeave: () => {} });
    }
    ReactDOM.createRoot(f).render(React.createElement(W));
  }, { code: CODE });
  await p.waitForTimeout(1800);

  // ── 1. A telefon beküldő-panelt mutat ──
  console.log('\n===== 1. A TELEFON BEKÜLDŐ-PANELT MUTAT =====');
  ok(/eredmény beküldése/i.test(await phoneTxt(p)), 'a telefonon ott a „Eredmény beküldése" panel');
  ok(/Sere/.test(await phoneTxt(p)) && /Kecsi/.test(await phoneTxt(p)), 'és a meccs két játékosa látszik');
  ok(!/BEKÜLDÖTT EREDMÉNY/.test(await hostTxt(p)), 'a hoston MÉG NINCS jóváhagyó sáv (nincs beküldés)');

  // A bracket VÉLETLENszerűen sorsol — kiolvassuk a jelenlegi meccs orientációját,
  // hogy a rows[0] (bal = p1) tényleg a meccs p1-je legyen.
  const cm = await p.evaluate(c => {
    const bp = window.__fbStore['rooms'][c].bp2State;
    const r0 = Array.isArray(bp.seRounds) ? bp.seRounds[0] : Object.values(bp.seRounds)[0];
    const m = Array.isArray(r0) ? r0[0] : Object.values(r0)[0];
    return { p1id: m.p1.id, p2id: m.p2.id, p1name: m.p1.name, p2name: m.p2.name };
  }, CODE);

  // ── 2. A telefonon beállítjuk az eredményt és beküldjük ──
  console.log('\n===== 2. BEKÜLDÉS =====');
  // Sere számlálóján 7×„+", Kecsi 0 marad. A CupCounter: [−, szám, +].
  await p.evaluate(async () => {
    const rows = [...document.querySelectorAll('#__phone div')].filter(d => {
      const k = [...d.children];
      return k.length === 3 && k[0].tagName === 'BUTTON' && k[2].tagName === 'BUTTON'
        && (k[0].textContent || '').trim() === '−' && (k[2].textContent || '').trim() === '+';
    });
    const plus = [...rows[0].children][2];
    for (let i = 0; i < 7; i++) { plus.click(); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); }
  });
  await p.waitForTimeout(200);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__phone button')].find(x => /Beküldés a hostnak/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(700);
  const sub = (await store(p)).bp2Submit;
  ok(sub && sub.p1 === 7 && sub.p2 === 0, 'a szoba bp2Submit mezője megtelt (7–0)', sub && (sub.p1 + '–' + sub.p2));
  ok(sub && sub.p1id === cm.p1id && sub.p2id === cm.p2id, 'a beküldés a meccs két játékosának id-jét viszi', sub && (sub.p1id + '/' + sub.p2id));
  ok(/Elküldve|jóváhagyására vár/.test(await phoneTxt(p)), 'a telefon „várakozás" állapotot mutat');

  // ── 3. A hoston megjelenik a jóváhagyó sáv ──
  console.log('\n===== 3. A HOST JÓVÁHAGYÓ SÁV =====');
  const ht = await hostTxt(p);
  ok(/BEKÜLDÖTT EREDMÉNY/.test(ht), 'a hoston ott a „📱 BEKÜLDÖTT EREDMÉNY" sáv', /BEKÜLDÖTT/.test(ht));
  ok(/7\s*–\s*0/.test(ht), 'és a beküldött eredmény (7 – 0)', (ht.match(/\d\s*–\s*\d/) || ['nincs'])[0]);
  ok(/Elfogadom és rögzítem/.test(ht), 'van „Elfogadom és rögzítem" gomb');

  // ── 4. Elfogadás → bajnok + pont + bp2Submit törlődik ──
  console.log('\n===== 4. ELFOGADÁS → RÖGZÍTÉS =====');
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__host button')].find(x => /Elfogadom és rögzítem/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(1400);
  ok(/Bajnok|🏆/.test(await hostTxt(p)), '2 főnél az első meccs a döntő — bajnokot hirdet', (await hostTxt(p)).slice(0, 70));
  const adv = await p.evaluate(() => window.__adv);
  // A 7 kortyot a p1 (a beküldő rows[0]) kapta → ő a NYERTES, a p2 a vesztes.
  ok(adv && adv.pm && adv.pm[cm.p1id] > 0, `a bajnok (${cm.p1name}) pontot kap (onAdvance pm)`, adv && JSON.stringify(adv.pm));
  ok(adv && adv.dm && adv.dm[cm.p2id] === 7, `a vesztes (${cm.p2name}) 7 kortyot kap (a pohár-különbség)`, adv && adv.dm && JSON.stringify(adv.dm));
  const sub2 = (await store(p)).bp2Submit;
  ok(!sub2, 'a bp2Submit törlődött a rögzítés után', sub2 ? 'MÉG OTT VAN' : 'törölve');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
