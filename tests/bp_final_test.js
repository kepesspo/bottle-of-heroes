// v10.336 — Beer Pong: a döntő, és a bajnokság utáni kísértet-push
//
// KÉT BEJELENTÉS, két különböző ok:
//
// 1. „Döntő mérkőzés: pohár szám / döntő mindig 1 meccs"
//    A „Visszavágó" kapcsoló szövege szerint minden meccs két menetes — a
//    megerősítő gomb viszont az egyenes kieséses ágban a DÖNTŐT is automatikusan
//    két menetre bontotta. A döntő mostantól MINDIG egy meccs, és saját
//    pohár-száma van (`finalCups`).
//
//    ⚠️ A döntő felismerése NEM az, hogy „egy meccs van a körben": 3 játékosnál
//    a 0. kör is egy meccs (a harmadik szabadkártyát kap), utána viszont még jön
//    a döntő. A 2. blokk pont ezt az esetet méri.
//
// 2. „Ha véget ért a bajnokság és utána megnyitjuk, akkor érkezik push üzenet"
//    A néző-képernyő az ELSŐ pillanatképnél is értesített: a feltétel
//    `!prev?.bpNotif` volt, `prev` pedig a szoba React-állapota, ami mountoláskor
//    még `null`. Így a szobában ÜLŐ, RÉGI `bpNotif` minden megnyitáskor újra
//    elsült. A fogódzó ezért egy MÁR BENT LÉVŐ értesítéssel nyit szobát.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

async function open(b) {
  const p = await b.newPage({ viewport: { width: 402, height: 1000 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

// A jatekot kozvetlenul mountoljuk, adott letszammal es beallitassal.
const mountBp = (p, names, cfg) => p.evaluate(({ names, cfg }) => {
  const cols = ['#E07A5F','#4FC2A0','#A78BFA','#5BA0DB','#E8A31E','#D96BA0'];
  const pl = names.map((n, i) => ({ id: 'p' + i, name: n, color: cols[i % cols.length], points:0, drinks:0 }));
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  let root = document.getElementById('__p'); if (root) root.remove();
  root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto';
  document.body.appendChild(root);
  window.__cupRows = () => [...document.querySelectorAll('#__p div')].filter(d => {
    const k = [...d.children];
    return k.length === 3 && k[0].tagName === 'BUTTON' && k[2].tagName === 'BUTTON'
      && (k[0].textContent || '').trim() === '\u2212' && (k[2].textContent || '').trim() === '+';
  });
  ReactDOM.createRoot(root).render(React.createElement(BeerPongGame, {
    gameIdx: 0, players: pl, gameMeta: { beerpongConfig: cfg }, roomCode: null, initialBpState: null,
    onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
}, { names, cfg });

// ⚠️ CSAK a meccs-lap felso cimke-sorat nezzuk (BRACKET · MECCS N · fazis).
// A teljes oldal szovegere szurni felrevezet: a lenti faag-nezet is kiirja,
// hogy „Döntő", tehat a `/DÖNTŐ/` az elodontonel is illeszkedne.
const labels = p => p.evaluate(() => {
  const el = [...document.querySelectorAll('#__p div')].find(d =>
    /MECCS \d/.test(d.innerText || '') && d.children.length >= 3 && (d.innerText || '').length < 70);
  return el ? (el.innerText || '').replace(/\s+/g, ' ') : '(nincs címke-sor)';
});

// A pohar-szamlalot a SAJAT szerkezete alapjan keressuk (− szam +), nem a
// gombok sorrendjebol: a lapon mas leptetok is vannak.
// A „+" annyiszor nyomva, amennyit enged — igy derul ki a plafon.
// ⚠️ KEPKOCKANKENT kattintunk. A React kotegel: 40 szinkron kattintas mind
// UGYANAZT a renderelt `value`-t latja, tehat a szamlalo egyet lepne csak.
// Ezert minden kattintas utan megvarjuk az ujrarajzolast, es UJRA lekerdezzuk
// a sort (a regi csomopont cserelodhet).
const cupCeiling = (p, which) => p.evaluate(async (which) => {
  const row = () => window.__cupRows()[which];
  if (window.__cupRows().length < 2) return null;
  let last = -1;
  for (let i = 0; i < 40; i++) {
    const r = row(); if (!r) break;
    const k = [...r.children];
    k[2].click();
    await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
    const v = parseInt(([...row().children][1].textContent || '').trim(), 10);
    if (v === last) break;   // beert a plafonra
    last = v;
  }
  return last;
}, which);
const confirm = p => p.evaluate(() => {
  const x = [...document.querySelectorAll('#__p button')].find(y => /nyert — tovább|Döntetlen megerősítése/.test(y.textContent || ''));
  if (!x || x.disabled) return 'NINCS'; x.click(); return 'ok';
});
const resetCups = p => p.evaluate(async () => {
  for (let w = 0; w < 2; w++) {
    for (let i = 0; i < 40; i++) {
      const r = window.__cupRows()[w]; if (!r) break;
      const k = [...r.children];
      if ((k[1].textContent || '').trim() === '0') break;
      k[0].click();
      await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
    }
  }
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  let p = await open(b);

  // ── 1. KET JATEKOS: az elso meccs MAR a donto ──
  console.log('\n===== 1. KET JATEKOS — AZ ELSO MECCS A DONTO =====');
  await mountBp(p, ['Sere', 'Kecsi'], { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:6, visszavago:true, matchMinutes:0 });
  await p.waitForTimeout(1500);
  const t1 = await labels(p);
  ok(/DÖNTŐ/.test(t1), 'a lap kiírja, hogy ez a DÖNTŐ', t1.slice(0, 90));
  ok(!/1\. MECCS|VISSZAVÁGÓ/.test(t1), 'NINCS „1. MECCS" felirat — a döntő egy meccs', t1.slice(0, 90));
  const ceil1 = await cupCeiling(p, 0);
  ok(ceil1 === 6, 'a döntőben a saját pohár-szám a plafon (finalCups=6)', ceil1);

  // ...es a megerosites AZONNAL bajnokot hirdet, nem indit masodik menetet
  await p.waitForTimeout(200);
  ok(await confirm(p) === 'ok', 'a megerősítés élő');
  await p.waitForTimeout(1200);
  const after1 = await labels(p);
  ok(/BAJNOK|Bajnok|🏆/.test(after1) || !/DÖNTŐ/.test(after1),
     'egyetlen megerősítés lezárta a bajnokságot — nem jött visszavágó', after1.slice(0, 110));

  // ── 2. HAROM JATEKOS: a 0. kor IS egy meccs, de az meg NEM a donto ──
  // Ez a blokk a naiv „egy meccs van a korben" felismerest bukná.
  console.log('\n===== 2. HAROM JATEKOS — A 0. KOR NEM A DONTO =====');
  await mountBp(p, ['Sere', 'Kecsi', 'Vivi'], { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:4, visszavago:true, matchMinutes:0 });
  await p.waitForTimeout(1500);
  const t2 = await labels(p);
  ok(!/DÖNTŐ/.test(t2), 'az elődöntő NEM döntő (pedig egy meccs van a körben)', t2.slice(0, 90));
  const ceil2 = await cupCeiling(p, 0);
  ok(ceil2 === 10, 'ott még a normál pohár-szám a plafon', ceil2);
  ok(/1\. MECCS/.test(t2), 'ott VAN két menet (a visszavágó be van kapcsolva)', t2.slice(0, 90));

  // vegigjatsszuk az elodontot (ket menet), majd a dontobe erunk
  await confirm(p); await p.waitForTimeout(700);      // 1. menet
  await resetCups(p); await cupCeiling(p, 0);          // a 2. menetet is megnyerjuk
  await p.waitForTimeout(200);
  await confirm(p); await p.waitForTimeout(1200);
  const t3 = await labels(p);
  ok(/DÖNTŐ/.test(t3), 'a következő meccs MÁR a döntő', t3.slice(0, 90));
  const ceil3 = await cupCeiling(p, 0);
  ok(ceil3 === 4, 'és ott a döntő pohár-száma él (finalCups=4)', ceil3);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 3. A KISERTET-PUSH: mar BENT levo ertesitessel nyitunk szobat ──
  console.log('\n===== 3. A BAJNOKSAG UTANI KISERTET-PUSH =====');
  p = await open(b);
  const notif = await p.evaluate(async () => {
    const code = '660044';
    // A szoba ugy all, ahogy a bajnoksag vege utan: van champion, ES ott ul
    // az utolso „Kovetkezo meccs!" ertesites.
    window.__fbStore['rooms'] = { [code]: {
      code, players: [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                      { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 }],
      gameIdx: 0, turn: 0, round: 1, selectedGames: ['erem'],
      bpNotif: { p1:'Sere', p2:'Kecsi', ts: Date.now() - 60000 },
      gameEvent: { correct:true, playerName:'Sere', drinks:0, ts: Date.now() - 90000 },
      roundEvent: { round: 3, ts: Date.now() - 120000 },
    } };
    const seen = [];
    window._bohShowNotif = (title, body) => { seen.push(title + ' | ' + body); };
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(ObserverWatching, {
      code, observerName: 'Vivi', onLeave: () => {} }));
    await new Promise(r => setTimeout(r, 2200));
    return { seen: seen.slice(), body: document.getElementById('__p').innerText };
  });
  ok(notif.seen.length === 0,
     'szobanyitáskor NEM jön push a szobában ülő régi értesítésből',
     notif.seen.join(' // ') || 'egy sem');
  ok(!/Kész!|NYERTES|ISZIK/.test(notif.body || ''),
     'és a régi eredmény-banner sem ugrik fel', (notif.body || '').replace(/\s+/g, ' ').slice(0, 80));

  // ...de egy VALODI, uj ertesites atmegy
  const live = await p.evaluate(async () => {
    const seen = [];
    window._bohShowNotif = (t, b) => { seen.push(t + ' | ' + b); };
    await firebase.firestore().collection('rooms').doc('660044')
      .update({ bpNotif: { p1:'Vivi', p2:'Sere', ts: Date.now() } });
    await new Promise(r => setTimeout(r, 900));
    return seen;
  });
  ok(live.length === 1 && /Vivi/.test(live[0]),
     'kontroll: egy VALÓDI új értesítés viszont átmegy', live.join(' // ') || 'egy sem');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
