// v10.374 — Imposztor: telefonról is játszható (titkos szerep + szavazás)
//
// A host koordinál, minden telefon a SAJÁT szerepét látja (nincs körbeadás).
// A titkos szerep a per-player `impRole` mezőben megy le: az imposztor `word:null`-t
// kap, a csapat a szót. A globális `impState` CSAK a fázist viszi — az imposztor
// kilétét nem.
//
// Fogódzók:
//  1) a szerepek helyesen szinkronizálódnak (imposztor: word=null; csapat: word)
//  2) a telefon a helyes szerepet mutatja (IMPOSZTOR vs a szó)
//  3) kész-jelzés: a telefon jelöl, a host látja
//  4) szavazás → könyvelés: mind az imposztorra szavaz → onResult/onAdvance stimmel
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
            { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
            { id:'p2', name:'Vivi', color:'#A78BFA', points:0, drinks:0 }];
const CODE = '880022';

const store = p => p.evaluate(() => window.__fbStore['rooms']['880022'] || {});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1500 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // HOST + egy TELEFON (a phone-player nevét paraméterből választjuk mount után)
  await p.evaluate(({ pl, code }) => {
    window.__fbStore['rooms'] = { [code]: { code, players: pl, gameIdx: 0, selectedGames: ['imposztor'] } };
    window.__res = null; window.__adv = null;
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:740px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(ImposztorGame, {
      gameIdx: 0, players: pl, roomCode: code,
      onResult: r => { window.__res = r; }, onAdvance: (dm, pm) => { window.__adv = { dm, pm }; } }));
    // TELEFON — a szoba pillanatképét figyeli
    const f = document.createElement('div'); f.id = '__phone';
    f.style.cssText = 'position:absolute;left:0;top:760px;width:402px;height:700px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(f);
    window.__setPhoneName = null;
    function W() {
      const [room, setRoom] = React.useState(() => window.__fbStore['rooms'][code]);
      const [nm, setNm] = React.useState(null);
      window.__setPhoneName = setNm;
      React.useEffect(() => firebase.firestore().collection('rooms').doc(code).onSnapshot(s => setRoom(s.data() || null)), []);
      if (!room) return null;
      return React.createElement(ImposztorObserverView, { code, room, observerName: nm });
    }
    ReactDOM.createRoot(f).render(React.createElement(W));
  }, { pl: PL, code: CODE });
  await p.waitForTimeout(1500);

  // ── 1. A szerepek helyesen szinkronizálódtak ──
  console.log('\n===== 1. SZEREPEK — imposztor: word=null, csapat: van szó =====');
  const roles = (await store(p)).impRole || {};
  const impIds = Object.keys(roles).filter(id => roles[id].imp);
  const crewIds = Object.keys(roles).filter(id => !roles[id].imp);
  ok(impIds.length === 1, 'pontosan 1 imposztor van (3 játékosnál)', impIds.length);
  ok(impIds.every(id => roles[id].word == null), '⚠️ az imposztor NEM kapja meg a szót (word=null)', JSON.stringify(impIds.map(id=>roles[id].word)));
  const theWord = crewIds.length ? roles[crewIds[0]].word : null;
  ok(!!theWord && crewIds.every(id => roles[id].word === theWord), 'a csapat mind UGYANAZT a szót kapja', theWord);
  const impName = (PL.find(x => x.id === impIds[0]) || {}).name;
  const crewName = (PL.find(x => x.id === crewIds[0]) || {}).name;

  // ── 2. A telefon a helyes szerepet mutatja ──
  console.log('\n===== 2. TELEFON — a saját szerep (IMPOSZTOR vs a szó) =====');
  // csapat-telefon
  await p.evaluate(n => window.__setPhoneName(n), crewName);
  await p.waitForTimeout(300);
  // "Ki vagy?" — a saját nevünkre nem kell kattintani, mert observerName kiválasztja; de biztos, ami biztos:
  await p.evaluate((n) => { const x=[...document.querySelectorAll('#__phone button')].find(y=>(y.textContent||'').trim()===n); if(x)x.click(); }, crewName);
  await p.waitForTimeout(200);
  // nyomd-tartsd a szerepet
  await p.evaluate(() => { const x=[...document.querySelectorAll('#__phone button')].find(y=>/Nyomd a szerepedhez/.test(y.textContent||'')); if(x){ x.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); } });
  await p.waitForTimeout(200);
  const crewTxt = await p.evaluate(() => (document.getElementById('__phone').innerText||'').replace(/\s+/g,' '));
  ok(crewTxt.includes(theWord), `a CSAPAT-telefon (${crewName}) a szót mutatja: „${theWord}"`, crewTxt.includes(theWord));
  ok(!/TE VAGY AZ IMPOSZTOR/.test(crewTxt), 'és NEM írja, hogy imposztor');

  // imposztor-telefon
  await p.evaluate(n => window.__setPhoneName(n), impName);
  await p.waitForTimeout(300);
  await p.evaluate((n) => { const x=[...document.querySelectorAll('#__phone button')].find(y=>(y.textContent||'').trim()===n); if(x)x.click(); }, impName);
  await p.waitForTimeout(200);
  await p.evaluate(() => { const x=[...document.querySelectorAll('#__phone button')].find(y=>/Nyomd a szerepedhez/.test(y.textContent||'')); if(x){ x.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true})); } });
  await p.waitForTimeout(200);
  const impTxt = await p.evaluate(() => (document.getElementById('__phone').innerText||'').replace(/\s+/g,' '));
  ok(/TE VAGY AZ IMPOSZTOR/.test(impTxt), `az IMPOSZTOR-telefon (${impName}) „IMPOSZTOR"-t mutat`, /IMPOSZTOR/.test(impTxt));
  ok(!impTxt.includes(theWord), 'és NEM látja a szót');

  // ── 3. Kész-jelzés: a telefon jelöl, a host látja ──
  console.log('\n===== 3. KÉSZ-JELZÉS =====');
  await p.evaluate(() => { const x=[...document.querySelectorAll('#__phone button')].find(y=>/Megvan, kész/.test(y.textContent||'')); if(x)x.click(); });
  await p.waitForTimeout(500);
  ok(((await store(p)).impReady || {})[impIds[0]] === true, 'a telefon „kész"-jelzése felkerült a szobába');
  const hostTxt3 = await p.evaluate(() => (document.getElementById('__host').innerText||'').replace(/\s+/g,' '));
  ok(/1\/3 kész/.test(hostTxt3), 'a host koordinátor „1/3 kész"-t mutat', (hostTxt3.match(/\d\/\d kész/)||['?'])[0]);

  // ── 4. Szavazás → könyvelés: mind az imposztorra szavaz ──
  console.log('\n===== 4. SZAVAZÁS → KÖNYVELÉS (imposztor lebukik) =====');
  // host: „Jöhet a szavazás"
  await p.evaluate(() => { const x=[...document.querySelectorAll('#__host button')].find(y=>/szavazás/i.test(y.textContent||'')); if(x)x.click(); });
  await p.waitForTimeout(500);
  // mindenki az imposztorra szavaz (a phone helyett közvetlen szoba-írással a 3-hoz)
  await p.evaluate((impId) => {
    const ref = firebase.firestore().collection('rooms').doc('880022');
    return ref.update({ ['impVote.p0']: impId, ['impVote.p1']: impId, ['impVote.p2']: impId });
  }, impIds[0]);
  await p.waitForTimeout(1800);
  const res = await p.evaluate(() => window.__res);
  const adv = await p.evaluate(() => window.__adv);
  ok(!!res && !!adv, 'a host lekönyvelte az eredményt (onResult + onAdvance)');
  ok(res && (res.losers||[]).some(x => x.id === impIds[0]), 'az imposztor a banner ISZIK oldalán (lebukott)', res && (res.losers||[]).map(x=>x.name).join(','));
  ok(adv && adv.dm && adv.dm[impIds[0]] === 3, 'az imposztor 3 kortyot kap a könyvelésben', adv && adv.dm && adv.dm[impIds[0]]);
  ok(adv && adv.pm && crewIds.every(id => adv.pm[id] === 1), 'a helyesen szavazó csapat +1 pontot kap', adv && JSON.stringify(adv.pm));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
