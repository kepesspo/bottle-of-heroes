// v10.334 — Időpárbaj: a stoppert a saját telefonon lehet nyomni
//
// A PROBLÉMA: ha a host egy laptop, a játékot senki nem tudta játszani — az
// indítás/megállítás csak a host képernyőjén volt.
//
// ⚠️ AMIT EZ A TESZT VALÓJÁBAN ŐRIZ, és amiért két készülékkel ÉS mesterséges
// késleltetéssel fut: a mért idő nem tartalmazhatja a hálózati köridőt.
// Ha a stoppert a host mérné (indítás- és megállítás-eseményt küldve, mint a
// Tappernél a nyomva tartást), akkor 250 ms-os késleltetésnél egy 1,5 mp-es
// mérés ~2,0 mp-nek látszana — a játék 0,1 mp felbontású, tehát merőben
// játszhatatlan lenne. Ezért a stopper a TELEFONON fut, és csak a KÉSZ
// eredmény megy fel.
//
// A második fogódzó: a „Stop" gombnak AZONNAL meg kell jelennie az indítás
// után, még a pillanatkép visszaérése ELŐTT. Ha a telefon a szoba fázisára
// várna, a mérés első negyed másodpercében nem lehetne megállítani.
// (Ugyanaz a lecke, mint a Blackjack optimista visszhangjánál — v10.331.)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'p0', name:'Sere',  color:'#E07A5F', points:0, drinks:0 },
            { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
            { id:'p2', name:'Vivi',  color:'#A78BFA', points:0, drinks:0 }];
const CODE = '770011';
const LAG = 250;   // a valodi halozati korido nagysagrendje

const st = p => p.evaluate(() => (window.__fbStore['rooms']['770011'].idoState) || null);

// A telefon gombjai — felirat szerint (a host tablaja kulon konteneren ul)
const phoneBtn = (p, re) => p.evaluate((re) => {
  const x = [...document.querySelectorAll('#__phone button')].find(y => new RegExp(re).test((y.textContent||'').trim()));
  return x ? (x.textContent||'').replace(/\s+/g,' ').trim() : null;
}, re.source || re);
const clickPhone = (p, re) => p.evaluate((re) => {
  const x = [...document.querySelectorAll('#__phone button')].find(y => new RegExp(re).test((y.textContent||'').trim()));
  if (!x) return 'NINCS'; x.click(); return 'ok';
}, re.source || re);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1400 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ pl, code, lag }) => {
    window.__fbStore['rooms'] = { [code]: { code, players: pl, gameIdx: 0, selectedGames: ['idopárbaj'] } };
    window.__res = null; window.__adv = null;
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    // HOST tabla — a valodi topologia: o irja es figyeli ugyanazt a szobat
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:700px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(IdoparbajGame, {
      gameIdx: 0, challenger: pl[0], opponent: pl[1], roomCode: code,
      onResult: r => { window.__res = r; }, onAdvance: (dm, pm) => { window.__adv = { dm, pm }; } }));
    // TELEFON — a pillanatkep KESVE er ide, mint a valosagban
    const f = document.createElement('div'); f.id = '__phone';
    f.style.cssText = 'position:absolute;left:0;top:700px;width:402px;height:700px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(f);
    function W() {
      const [room, setRoom] = React.useState(() => window.__fbStore['rooms'][code]);
      React.useEffect(() => firebase.firestore().collection('rooms').doc(code)
        .onSnapshot(s => { const d = s.data() || null; setTimeout(() => setRoom(d), lag); }), []);
      if (!room) return null;
      return React.createElement(IdoparbajObserverView, { code, room, observerName: null });
    }
    ReactDOM.createRoot(f).render(React.createElement(W));
  }, { pl: PL, code: CODE, lag: LAG });
  await p.waitForTimeout(LAG + 1200);

  // ── 1. a host leküldi a párost és a célt ──
  console.log('\n===== 1. A HOST LEKULDI A PAROST =====');
  const s0 = await st(p);
  ok(!!s0, 'van idoState a szobában');
  ok(s0 && s0.p1 && s0.p1.id === 'p0' && s0.p2 && s0.p2.id === 'p1',
     'a páros a HOSTTÓL jön (nem a telefon találgat)', JSON.stringify([s0 && s0.p1, s0 && s0.p2]));
  ok(s0 && typeof s0.target === 'number' && s0.target >= 5 && s0.target <= 30,
     'a cél idő is lemegy — a telefon látja, mire céloz', s0 && s0.target);
  ok(s0 && s0.phase === 'idle', 'a fázis „idle"-ről indul', s0 && s0.phase);
  // Az observer-valto BE VAN kotve — enelkul a telefon a sima nezo-kepernyot
  // kapna, es a jatek ugyanugy jatszhatatlan maradna. Az azonosito EKEZETES
  // (`idopárbaj`), egy elgepeles itt nemán semmit nem csinalna.
  ok(fs.readFileSync(ROOT + '/app.src.html', 'utf8').includes("_ovCurG === 'idopárbaj'"),
     'az observer-váltó ismeri az Időpárbajt (ékezetes azonosító)');

  // ── 2. „Ki vagy?" — a telefon a páros KÉT tagját kínálja ──
  console.log('\n===== 2. KI VAGY? =====');
  const pick = await p.evaluate(() => [...document.querySelectorAll('#__phone button')]
    .map(x => (x.textContent||'').replace(/\s+/g,' ').trim()).filter(Boolean));
  ok(/Ki vagy\?/.test(await p.evaluate(() => document.getElementById('__phone').innerText)),
     'a telefonon a „Ki vagy?" választó áll');
  ok(pick.length === 2 && pick.includes('Sere ›') === false, 'pontosan két név közül lehet választani', JSON.stringify(pick));
  ok(pick.some(x => /Sere/.test(x)) && pick.some(x => /Kecsi/.test(x)),
     'a párosítás két tagja — nem a harmadik játékos', JSON.stringify(pick));
  ok(!pick.some(x => /Vivi/.test(x)), 'a párosításon kívüli Vivi NEM választható', JSON.stringify(pick));

  // ── 3. a mérés a TELEFONON fut — a hálózat nem tolja el ──
  console.log('\n===== 3. A MERES A TELEFONON FUT =====');
  await clickPhone(p, /Sere/);
  await p.waitForTimeout(300);
  ok(/CÉL IDŐ/.test(await p.evaluate(() => document.getElementById('__phone').innerText)),
     'kiválasztás után a telefonon ott a cél-lap');
  ok(await clickPhone(p, /Indítás/) === 'ok', 'van „Indítás" gomb, és élő');

  // A „Stop" AZONNAL kint van — meg mielott a pillanatkep visszaerne.
  await p.waitForTimeout(60);
  ok(!!(await phoneBtn(p, /Stop/)), `a „Stop" AZONNAL megjelenik (${LAG} ms-os pillanatkép-késés ELŐTT)`,
     await phoneBtn(p, /Stop/));

  // ⚠️ A HOST kepernyojen ilyenkor NEM lehet „Stop": az o `startRef`-je ures,
  // tehat a `Date.now() - null` egy 1970 ota eltelt masodperceket tartalmazo
  // szemetet konyvelne el mert idokent.
  await p.waitForTimeout(LAG + 350);
  const hostRun = await p.evaluate(() => {
    const el = document.getElementById('__host');
    return { txt: (el.innerText || '').replace(/\s+/g, ' '),
             stop: [...el.querySelectorAll('button')].some(x => /Stop/.test(x.textContent || '')) };
  });
  ok(hostRun.stop === false, 'a host tábláján NINCS „Stop", amíg a telefon mér', hostRun.txt.slice(0, 80));
  ok(/saját telefonján/.test(hostRun.txt), 'a host ki is írja, hogy a telefonon megy', hostRun.txt.slice(0, 80));

  const HOLD = 1500;
  await p.waitForTimeout(Math.max(100, HOLD - 60 - (LAG + 350)));
  const tap = Date.now();
  await clickPhone(p, /Stop/);
  await p.waitForTimeout(LAG + 900);
  const s1 = await st(p);
  const measured = s1 && s1.t1;
  ok(typeof measured === 'number', 'a mért idő felkerült a szobába', measured);
  // A LENYEG: a keslelteteshez kepest is a VALODI tartast merte. Ha a host
  // merne, ~2 x LAG-gal tobb jonne ki.
  ok(Math.abs(measured - HOLD / 1000) < 0.35,
     `a mért idő a VALÓDI tartás (${(HOLD/1000).toFixed(1)} mp), nem tartás + hálózat`,
     measured + ' mp');
  ok(measured < (HOLD + 2 * LAG) / 1000 - 0.2,
     'kontroll: ha a host mérné, legalább ' + ((HOLD + 2*LAG)/1000).toFixed(1) + ' mp jönne ki', measured);
  ok(s1 && s1.phase === 'p1done', 'a host átlépett a második játékosra', s1 && s1.phase);

  // ── 4. a telefon tudja, hogy nem ő jön ──
  console.log('\n===== 4. SORRA VARAS =====');
  const phoneTxt = await p.evaluate(() => document.getElementById('__phone').innerText);
  ok(!(await phoneBtn(p, /Indítás|Stop/)), 'Sere telefonján nincs több gomb — lejátszotta', phoneTxt.replace(/\n/g,' | ').slice(0,90));

  // ── 5. a masodik jatekos is a telefonrol ──
  console.log('\n===== 5. A MASODIK JATEKOS IS TELEFONROL =====');
  await clickPhone(p, /Mégsem/);
  await p.waitForTimeout(250);
  await clickPhone(p, /Kecsi/);
  await p.waitForTimeout(300);
  ok(await clickPhone(p, /Indítás/) === 'ok', 'Kecsi telefonján is van „Indítás"');
  await p.waitForTimeout(600);
  await clickPhone(p, /Stop/);
  await p.waitForTimeout(LAG + 1400);
  const s2 = await st(p);
  ok(typeof (s2 && s2.t2) === 'number', 'a második idő is felkerült', s2 && s2.t2);
  ok(s2 && s2.phase === 'result', 'a kör lezárult', s2 && s2.phase);

  const out = await p.evaluate(() => ({ res: window.__res, adv: window.__adv }));
  ok(!!out.res && !!out.adv, 'a host könyvelt (onResult + onAdvance) — telefonról játszva is');
  const tgt = s2.target;
  const expWin = Math.abs(s2.t1 - tgt) <= Math.abs(s2.t2 - tgt) ? 'Sere' : 'Kecsi';
  ok(out.res && (out.res.winners||[])[0] && out.res.winners[0].name === expWin,
     `a közelebbi idő nyer (${s2.t1} / ${s2.t2} · cél ${tgt}) → ${expWin}`,
     out.res && (out.res.winners||[])[0] && out.res.winners[0].name);
  const winId = expWin === 'Sere' ? 'p0' : 'p1', loseId = expWin === 'Sere' ? 'p1' : 'p0';
  ok(out.adv && out.adv.pm && out.adv.pm[winId] === 1, 'a győztes pontot kap', JSON.stringify(out.adv && out.adv.pm));
  ok(out.adv && out.adv.dm && out.adv.dm[loseId] === 1, 'a vesztes kortyot kap', JSON.stringify(out.adv && out.adv.dm));

  // ── 6. a KOZOS szoba-iras: a `db` NEM lathato az app szkriptjebol ──
  // Ez a hiba tette hasznalhatatlanna a telefonos jatekot, es NEMA volt: a
  // `var db` a Firebase-init IIFE-jeben ul (kulon <script>), tehat a bare `db`
  // hivasok `typeof db === 'undefined'` orzoje MINDIG igaz volt — a fuggveny
  // visszatert, hibauzenet nelkul. Merve: a Tapper telefonos nyomasa utan a
  // szoba `tapperInput` mezoje `undefined` maradt.
  console.log('\n===== 6. A KOZOS SZOBA-IRAS (bohRoomRef) =====');
  const wrote = await p.evaluate(async () => {
    const code = '990033';
    window.__fbStore['rooms'][code] = { code, players: [
      { id:'p0', name:'Sere', color:'#E07A5F' }, { id:'p1', name:'Kecsi', color:'#4FC2A0' }] };
    const ref = (typeof bohRoomRef === 'function') ? bohRoomRef(code) : null;
    if (!ref) return { helper: false };
    await ref.update({ tapperInput: { Sere: true } });
    return { helper: true, landed: window.__fbStore['rooms'][code].tapperInput };
  });
  ok(wrote.helper, 'van közös `bohRoomRef` — nem bare `db`');
  ok(wrote.landed && wrote.landed.Sere === true, 'és tényleg a szobába ír', JSON.stringify(wrote.landed));
  // A HIBA ALAIRASA a `typeof db === 'undefined'` orzo: az app szkriptjeben ez
  // MINDIG igaz, tehat a mogotte allo iras soha nem futott le. Egy ilyen sem
  // maradhat — ha valaki ujra igy irna, itt bukik.
  const guards = fs.readFileSync(ROOT + '/app.src.html', 'utf8')
    .split('\n').filter(l => /typeof db\s*[!=]==\s*'undefined'/.test(l));
  ok(guards.length === 0, 'sehol nincs `typeof db === undefined` őrző (a néma írás aláírása)',
     guards.map(l => l.trim().slice(0, 60)).join(' | ') || 'egy sincs');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
