// v10.240 — Ország-Város: a host–telefon kapcsolat két hibája
//
// TÜNET volt: a host továbbnyomta, a telefonos nézet nem reagált, beakadt.
//
// 1) VÉGTELEN ÍRÁSI HUROK
//    A host a beérkezett válaszokat `setAnswers(prev => ({...prev, ...na}))`-vel
//    tette el — ez MINDIG új objektumot ad. Az `answers` viszont függősége
//    annak az effektnek, amelyik kiírja az ovfjState-et a szobába:
//    írás → pillanatkép → új objektum → írás → …
//    Javítás előtt mérve: 2 másodperc alatt ~14 700 írás ugyanarra a
//    dokumentumra. A Firestore ~1 írás/mp-et bír tartósan, ezért a host
//    fázisváltása egyszerűen nem ért oda a telefonokhoz.
//
// 2) A SZOBA-FIGYELŐ NEM ÉPÜLT ÚJRA
//    A subscribeRoom nem adott hibakezelőt az onSnapshot-nak. A Firestore a
//    hibás figyelőt megszünteti — kezelő nélkül a képernyő csendben befagy.
//
// Ez a teszt mindkettőt méri, nem "ránézésre" ellenőrzi.
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

const click = (p, re) => p.evaluate(r => {
  const rx = new RegExp(r);
  const b = [...document.querySelectorAll('button')].find(x => rx.test((x.innerText || '').replace(/\s+/g, ' ')));
  if (b) { b.click(); return true; }
  return false;
}, re.source);

const bodyTxt = p => p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1200 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);

  // ══ 1. ÍRÁSI HUROK ══
  console.log('\n===== 1. NINCS ÍRÁSI HUROK =====');
  await p.evaluate(() => {
    window.__syncCount = 0;
    const orig = window.syncRoom;
    window.syncRoom = function (code, data) { window.__syncCount++; return orig(code, data); };
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;overflow:auto;padding:12px;box-sizing:border-box';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(OVFJGame, {
      players: [{ id:'a', name:'Alfa', color:'#E07A5F' }, { id:'b', name:'Beta', color:'#4FC2A0' }],
      gameIdx: 0, roomCode: '123456',
      gameMeta: { ovfjConfig: { rounds: 3, roundTime: 90 } },
      onAdvance: () => {}, onResult: () => {},
    }));
  });
  await p.waitForTimeout(1400);
  // Beta "csatlakozott telefonrol" — igy a host is szamit ra
  await p.evaluate(() => firebase.firestore().collection('rooms').doc('123456')
    .set({ ovfjTakenIds: ['b'] }, { merge: true }));
  await click(p, /Alfa/); await p.waitForTimeout(500);
  await click(p, /Én vagyok/); await p.waitForTimeout(900);
  ok(/SZOBAKÓD/.test(await bodyTxt(p)), 'a host kiválasztása után lobby');
  await click(p, /Kezdés/);
  await p.waitForTimeout(5200); // 4 mp betűsorsolás
  ok(/kategória kész/.test(await bodyTxt(p)), 'írási fázis elindult');

  // jojjon egy telefonos valasz
  const before = await p.evaluate(() => window.__syncCount);
  await p.evaluate(async () => {
    const st = window.__fbStore['rooms']['123456'].ovfjState;
    await firebase.firestore().collection('rooms').doc('123456').set({
      ovfjA_b: { pid:'b', sess: st.sess, round: st.round, done:true, doneAt: Date.now(),
                 orszag:'Anglia', varos:'Aszód', allat:'Antilop' },
    }, { merge: true });
  });
  await p.waitForTimeout(300);
  const mid = await p.evaluate(() => window.__syncCount);
  await p.waitForTimeout(2000);
  const after = await p.evaluate(() => window.__syncCount);
  ok(after - mid <= 5, 'a beérkezett válasz után NEM ír folyamatosan',
     `2 mp alatt ${after - mid} írás (a hiba idején ~14 700)`);
  ok(mid - before <= 6, 'a válasz feldolgozása is néhány írás', `${mid - before}`);

  // A valasz tenyleg atment: a host kiirta a sajat ovfjState-jebe (ezt latja a
  // tobbi telefon), es a szamlalo is lepett. A felirat onmagaban keves lenne.
  const landed = await p.evaluate(() => {
    const st = window.__fbStore['rooms']['123456'].ovfjState || {};
    return { hasB: !!(st.answers && st.answers.b), word: st.answers && st.answers.b && st.answers.b.orszag };
  });
  ok(landed.hasB && landed.word === 'Anglia', 'a válasz bekerült a host által kiírt ovfjState-be', JSON.stringify(landed));
  ok(/1\/2 játékos kész/.test(await bodyTxt(p)), 'a host számlálója is lépett',
     ((await bodyTxt(p)).match(/\d\/\d játékos kész/) || ['—'])[0]);
  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));

  // ══ 1b. A HOST KÖR VÉGI KÉPERNYŐJE (v10.303-304) ══
  // Vegigvisszuk az elso kort, es megnezzuk, mi all a host eredmeny-lapjan:
  // harom csempe, "Mit irtak?" visszanezes, es a KOVETKEZO kor szoszama.
  console.log('\n===== 1b. HOST KÖR VÉGE =====');
  await click(p, /Kész vagyok/); await p.waitForTimeout(1200);
  ok(/Szavazás/.test(await bodyTxt(p)), 'a host is beküldött → szavazás',
     (await bodyTxt(p)).slice(0, 60));
  await click(p, /Befejezés/); await p.waitForTimeout(1400);
  const veg = await bodyTxt(p);
  ok(/kör vége/.test(veg), 'eljutottunk a kör végi képernyőre', veg.slice(0, 60));

  // A csempe-feliratok `textTransform:uppercase`-szel jelennek meg, es az
  // innerText a RENDERELT szoveget adja vissza — ezert kis/nagybetu-fuggetlen.
  ok(/ebben a körben/i.test(veg) && /összesen/i.test(veg) && /helyezés/i.test(veg),
     'kint a három csempe (körös pont / összesen / helyezés)',
     (veg.match(/EBBEN A KÖRBEN|ÖSSZESEN|HELYEZÉS/gi) || []).join(', '));

  // A KOVETKEZO kor szoszama: eddig csak a lobbyban lehetett allitani.
  ok(/Hány szó egy kategóriához/.test(veg),
     'a következő kör szószáma is beállítható', /Hány szó/.test(veg) ? 'ott a választó' : 'NINCS');

  // Visszanezes: a gomb kinyitja, es tenyleg latszik, amit a telefon irt.
  ok(/Mit írtak\?/.test(veg), 'ott a „Mit írtak?" gomb');
  await click(p, /Mit írtak/); await p.waitForTimeout(700);
  const nyitva = await bodyTxt(p);
  ok(/Anglia/.test(nyitva), 'a panel kiírja a beküldött szavakat', /Anglia/.test(nyitva) ? 'Anglia látszik' : 'NEM látszik');
  // readOnly: a visszanezesben NINCS ertekelo gomb
  const ertekelok = await p.evaluate(() =>
    document.querySelectorAll('#__p button[aria-label="Elfogadom"], #__p button[aria-label="Nem fogadom el"]').length);
  ok(ertekelok === 0, 'a visszanézésben nincsenek értékelő gombok (readOnly)', ertekelok + ' db');
  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));

  // ══ 2. A SZOBA-FIGYELŐ ÚJRAÉPÜL ══
  console.log('\n===== 2. A SZOBA-FIGYELŐ ÚJRAÉPÜL HIBA UTÁN =====');
  const rec = await p.evaluate(async () => {
    window.__seen = [];
    const unsub = window.subscribeRoom('999999', d => window.__seen.push(d ? (d.marker || null) : null));
    await firebase.firestore().collection('rooms').doc('999999').set({ marker: 1 }, { merge: true });
    return { unsubIsFn: typeof unsub === 'function' };
  });
  ok(rec.unsubIsFn, 'a subscribeRoom leiratkozó függvényt ad vissza');
  await p.waitForTimeout(200);
  ok((await p.evaluate(() => window.__seen)).includes(1), 'a friss adat megérkezik');

  // szakitsuk el a figyelot — a Firestore hibat jelez, majd megszunteti
  const broken = await p.evaluate(() => window.__fbBreakListeners('rooms/999999'));
  ok(broken >= 1, 'a figyelő hibakezelőt kapott (a nélkül nem lenne mit elszakítani)', String(broken));

  // hiba kozben tortent iras: ezt meg nem latja
  await p.evaluate(() => firebase.firestore().collection('rooms').doc('999999').set({ marker: 2 }, { merge: true }));
  await p.waitForTimeout(200);
  ok(!(await p.evaluate(() => window.__seen)).includes(2), 'elszakadva tényleg nem lát semmit');

  // az elso ujraprobalkozas 1 mp mulva
  await p.waitForTimeout(1600);
  const seen = await p.evaluate(() => window.__seen);
  ok(seen.includes(2), 'újracsatlakozás után magától visszakapja az állapotot', JSON.stringify(seen));

  await p.evaluate(() => firebase.firestore().collection('rooms').doc('999999').set({ marker: 3 }, { merge: true }));
  await p.waitForTimeout(250);
  ok((await p.evaluate(() => window.__seen)).includes(3), 'és utána is követi a változásokat');
  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
