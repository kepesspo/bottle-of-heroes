// v10.426 — Imposztor-segítség: az imposztor a szó KATEGÓRIÁJÁT kapja, ha a
// beállító lapon be van kapcsolva (gameMeta.imposztorConfig.hint).
//
// Fogódzók:
//  1) a tipp-szótár MINDEN szóhoz ad tippet, és a tipp nem árulja el a szót
//  2) online: az imposztor szerepe viszi a tippet, a csapaté NEM (kontroll: kikapcsolva senkié)
//  3) a telefon az imposztornak mutatja a tippet, a csapatnak nem
//  4) offline körbeadás: a lenyomott lapon az imposztornál ott a tipp, a csapatnál nincs
//  5) a beállító lap kapcsolója a configba ír
// v10.427 — „Más szó" mód (undercover):
//  6) a kakukktojás-szó sosem a csapaté, és ahol lehet, UGYANABBÓL a kategóriából jön
//  7) online: az imposztor szót kap (nem null), a telefonja NEM mondja, hogy ő az imposztor;
//     a segítség ebben a módban nem jár, akkor sem, ha be volt kapcsolva
//  8) offline: mind a három lapon „TITKOS SZÓ", két különböző szó, az egyik pontosan egyszer
//  9) a beállító lapon a „Más szó" elrejti a Segítség sort, és a configba ír
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const PL = [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
            { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
            { id:'p2', name:'Vivi', color:'#A78BFA', points:0, drinks:0 }];

async function page(b) {
  const p = await b.newPage({ viewport: { width: 402, height: 1500 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html?screen=games', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}
// host + egy telefon ugyanarra a szobára
const mountOnline = (p, hint, code) => p.evaluate(({ pl, hint, code }) => {
  window.__fbStore['rooms'] = { [code]: { code, players: pl, gameIdx: 0, selectedGames: ['imposztor'] } };
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  const h = document.createElement('div'); h.id = '__host'; h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:700px;overflow:auto;background:#fff';
  document.body.appendChild(h);
  ReactDOM.createRoot(h).render(React.createElement(ImposztorGame, { gameIdx: 0, players: pl, roomCode: code,
    gameMeta: hint === null ? {} : { imposztorConfig: (typeof hint === 'object' ? hint : { hint }) }, onResult: () => {}, onAdvance: () => {} }));
  const f = document.createElement('div'); f.id = '__phone'; f.style.cssText = 'position:absolute;left:0;top:720px;width:402px;height:700px;overflow:auto;background:#fff';
  document.body.appendChild(f);
  function W() {
    const [room, setRoom] = React.useState(() => window.__fbStore['rooms'][code]);
    const [nm, setNm] = React.useState(null); window.__setPhoneName = setNm;
    React.useEffect(() => firebase.firestore().collection('rooms').doc(code).onSnapshot(s => setRoom(s.data() || null)), []);
    return room ? React.createElement(ImposztorObserverView, { code, room, observerName: nm }) : null;
  }
  ReactDOM.createRoot(f).render(React.createElement(W));
}, { pl: PL, hint, code });
const roles = (p, code) => p.evaluate(c => (window.__fbStore['rooms'][c] || {}).impRole || {}, code);
async function phoneHold(p, name) {
  await p.evaluate(n => window.__setPhoneName(n), name); await p.waitForTimeout(400);
  const btn = await p.$('#__phone button:has-text("Nyomd a szerepedhez")');
  const bx = await btn.boundingBox();
  await p.mouse.move(bx.x + bx.width / 2, bx.y + bx.height / 2); await p.mouse.down(); await p.waitForTimeout(250);
  const r = await p.evaluate(() => ({ t: document.getElementById('__phone').innerText, hint: (document.querySelector('#__phone [data-imp-hint]') || {}).innerText || null }));
  await p.mouse.up();
  return r;
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  console.log('\n===== 1. TIPP-SZÓTÁR =====');
  let p = await page(b);
  const dict = await p.evaluate(() => {
    const miss = IMPOSZTOR_SZAVAK.filter(w => !IMPOSZTOR_TIPPEK[w]);
    const leak = Object.entries(IMPOSZTOR_TIPPEK).filter(([w, h]) => h.toLowerCase().includes(w.toLowerCase()) || w.toLowerCase().includes(h.toLowerCase()));
    return { n: IMPOSZTOR_SZAVAK.length, miss, leak };
  });
  ok(dict.miss.length === 0, '⚠️ minden szóhoz van tipp', dict.miss.join(','));
  ok(dict.leak.length === 0, 'egyik tipp sem tartalmazza a szót (és fordítva)', JSON.stringify(dict.leak));

  console.log('\n===== 2–3. ONLINE: SZEREP + TELEFON =====');
  await mountOnline(p, true, '880101'); await p.waitForTimeout(1500);
  let r = await roles(p, '880101');
  const impId = Object.keys(r).find(id => r[id].imp), crewId = Object.keys(r).find(id => !r[id].imp);
  const word = r[crewId].word;
  const exp = await p.evaluate(w => IMPOSZTOR_TIPPEK[w], word);
  ok(r[impId].hint === exp && !!exp, 'az imposztor szerepe a szó kategóriáját viszi', `${word} → ${r[impId].hint}`);
  ok(Object.keys(r).filter(id => !r[id].imp).every(id => r[id].hint == null), 'a csapat szerepében nincs tipp');
  const ph = await phoneHold(p, PL.find(x => x.id === impId).name);
  ok(/TE VAGY AZ IMPOSZTOR/.test(ph.t) && ph.hint && ph.hint.includes(exp), '⚠️ az imposztor telefonján látszik a tipp', ph.hint);
  const pc = await phoneHold(p, PL.find(x => x.id === crewId).name);
  ok(pc.t.includes(word) && !pc.hint, 'a csapat telefonján a szó, tipp nélkül');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 2b. KONTROLL: KIKAPCSOLVA =====');
  p = await page(b);
  await mountOnline(p, null, '880102'); await p.waitForTimeout(1500);
  r = await roles(p, '880102');
  ok(Object.keys(r).length === 3 && Object.keys(r).every(id => r[id].hint == null), 'beállítás nélkül senki nem kap tippet');
  const ph2 = await phoneHold(p, PL.find(x => r[x.id].imp).name);
  ok(/TE VAGY AZ IMPOSZTOR/.test(ph2.t) && !ph2.hint, 'és az imposztor telefonján sincs');
  await p.close();

  console.log('\n===== 4. OFFLINE KÖRBEADÁS =====');
  for (const hint of [true, false]) {
    p = await page(b);
    await p.evaluate(({ pl, hint }) => {
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const h = document.createElement('div'); h.id = '__off'; h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:900px;background:#fff';
      document.body.appendChild(h);
      ReactDOM.createRoot(h).render(React.createElement(ImposztorGame, { gameIdx: 0, players: pl, gameMeta: { imposztorConfig: { hint } }, onResult: () => {}, onAdvance: () => {} }));
    }, { pl: PL, hint });
    await p.waitForTimeout(600);
    const seen = [];
    for (let i = 0; i < PL.length; i++) {
      const btn = await p.$('#__off button:has-text("Nyomd")'); const bx = await btn.boundingBox();
      await p.mouse.move(bx.x + bx.width / 2, bx.y + bx.height / 2); await p.mouse.down(); await p.waitForTimeout(200);
      const y2 = (await (await p.$('#__off button:has-text("Nyomd")')).boundingBox()).y;
      seen.push(await p.evaluate(() => ({ imp: /IMPOSZTOR/.test(document.getElementById('__off').innerText), hint: !!document.querySelector('#__off [data-imp-hint]') })));
      seen[seen.length - 1].moved = Math.round(y2 - bx.y);
      await p.mouse.up();
      await p.evaluate(() => [...document.querySelectorAll('#__off button')].find(x => /adom tovább/.test(x.textContent)).click()); await p.waitForTimeout(250);
    }
    const imps = seen.filter(x => x.imp), crew = seen.filter(x => !x.imp);
    if (hint) ok(imps.length === 1 && imps[0].hint && crew.every(x => !x.hint), 'bekapcsolva: az imposztor lapján tipp, a csapatén nincs', JSON.stringify(seen));
    else ok(imps.length === 1 && seen.every(x => !x.hint), 'kontroll: kikapcsolva senkinél nincs tipp', JSON.stringify(seen));
    // ⚠️ a tipp megjelenése nem tolhatja el a gombot az ujj alól (az első változatnál elengedte a tartást)
    ok(seen.every(x => Math.abs(x.moved) <= 4), 'a nyomva tartott gomb nem ugrik el a felfedéskor (≤ 4 px)', JSON.stringify(seen.map(x => x.moved)));
    await p.close();
  }

  console.log('\n===== 6. KAKUKKTOJÁS-SZÓ =====');
  p = await page(b);
  const odd = await p.evaluate(() => {
    let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const bad = [], offCat = [];
    IMPOSZTOR_SZAVAK.forEach(w => { for (let k = 0; k < 5; k++) {
      const o = imposztorOddWord(w, rnd);
      if (!o || o === w) bad.push(w);
      const sameExists = IMPOSZTOR_SZAVAK.some(x => x !== w && IMPOSZTOR_TIPPEK[x] === IMPOSZTOR_TIPPEK[w]);
      if (sameExists && IMPOSZTOR_TIPPEK[o] !== IMPOSZTOR_TIPPEK[w]) offCat.push(w + '→' + o);
    } });
    return { bad, offCat, ex: imposztorOddWord('Banán', () => 0) + ' / ' + imposztorOddWord('Delfin', () => 0.5) };
  });
  ok(odd.bad.length === 0, 'a kakukktojás-szó sosem azonos a csapat szavával', odd.bad.slice(0, 5).join(','));
  ok(odd.offCat.length === 0, '⚠️ ahol a kategóriában van más szó, onnan jön', odd.offCat.slice(0, 5).join(',') + ' · pl. ' + odd.ex);

  console.log('\n===== 7. ONLINE „MÁS SZÓ" =====');
  await mountOnline(p, { mode: 'undercover', hint: true }, '880103'); await p.waitForTimeout(1500);
  r = await roles(p, '880103');
  const uImp = Object.keys(r).find(id => r[id].imp), uCrew = Object.keys(r).filter(id => !r[id].imp);
  const cw = r[uCrew[0]].word, iw = r[uImp].word;
  ok(!!iw && iw !== cw && uCrew.every(id => r[id].word === cw), 'az imposztor MÁS szót kap, a csapat mind ugyanazt', `${cw} / ${iw}`);
  ok(Object.keys(r).every(id => r[id].hint == null), 'ebben a módban nincs segítség (akkor sem, ha be volt kapcsolva)');
  const pu = await phoneHold(p, PL.find(x => x.id === uImp).name);
  ok(pu.t.includes(iw) && !/TE VAGY AZ IMPOSZTOR/.test(pu.t) && /A TITKOS SZÓ/.test(pu.t), '⚠️ az imposztor telefonja a saját szavát mutatja, és nem árulja el, hogy ő az', iw);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 8. OFFLINE „MÁS SZÓ" =====');
  p = await page(b);
  await p.evaluate(({ pl }) => {
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const h = document.createElement('div'); h.id = '__off'; h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:900px;background:#fff';
    document.body.appendChild(h);
    window.__setPh = null;
    function W() { const [ph, setPh] = React.useState('play'); window.__setPh = setPh;
      return React.createElement(ImposztorGame, { gameIdx: 0, players: pl, gameMeta: { imposztorConfig: { mode: 'undercover' } }, onResult: () => {}, onAdvance: () => {} }); }
    ReactDOM.createRoot(h).render(React.createElement(W));
  }, { pl: PL });
  await p.waitForTimeout(600);
  const words = [];
  for (let i = 0; i < PL.length; i++) {
    const btn = await p.$('#__off button:has-text("Nyomd")'); const bx = await btn.boundingBox();
    await p.mouse.move(bx.x + bx.width / 2, bx.y + bx.height / 2); await p.mouse.down(); await p.waitForTimeout(200);
    words.push(await p.evaluate(() => { const t = document.getElementById('__off').innerText; const m = t.match(/TITKOS SZÓ\n+([^\n]+)/i); return { w: m ? m[1].trim() : null, imp: /IMPOSZTOR/.test(t) }; }));
    await p.mouse.up();
    await p.evaluate(() => [...document.querySelectorAll('#__off button')].find(x => /adom tovább/.test(x.textContent)).click()); await p.waitForTimeout(250);
  }
  const cnt = {}; words.forEach(x => { cnt[x.w] = (cnt[x.w] || 0) + 1; });
  ok(words.every(x => x.w && !x.imp), 'mindhárom lapon „TITKOS SZÓ" áll, sehol „IMPOSZTOR"', JSON.stringify(words));
  ok(Object.keys(cnt).length === 2 && Object.values(cnt).includes(1), 'két különböző szó, az egyik pontosan egyszer', JSON.stringify(cnt));
  await p.close();

  console.log('\n===== 5. BEÁLLÍTÓ LAP =====');
  p = await page(b);
  await p.evaluate(() => {
    window.__meta = {};
    const d = document.createElement('div'); d.id = '__cfg'; document.body.appendChild(d);
    function W() { const [m, setM] = React.useState({}); window.__meta = m;
      return React.createElement(GameConfigHost, { openId: 'imposztor', onClose: () => {}, gameMeta: m, setGameMeta: setM, playerCount: 4 }); }
    ReactDOM.createRoot(d).render(React.createElement(W));
  });
  await p.waitForTimeout(500);
  const sheet = await p.evaluate(() => document.body.innerText);
  ok(/Imposztor beállítások/.test(sheet) && /Imposztor-segítség/.test(sheet), 'a lap megnyílik');
  await p.evaluate(() => [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Be').click()); await p.waitForTimeout(200);
  ok(await p.evaluate(() => window.__meta.imposztorConfig && window.__meta.imposztorConfig.hint === true), 'a „Be" a gameMeta.imposztorConfig.hint-et kapcsolja');
  await p.evaluate(() => [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Más szó').click()); await p.waitForTimeout(200);
  ok(await p.evaluate(() => window.__meta.imposztorConfig.mode === 'undercover'), 'a „Más szó" a mode-ot állítja (9.)');
  ok(!/Imposztor-segítség/.test(await p.evaluate(() => document.body.innerText)), '„Más szó" módban a Segítség sor rejtve');
  await p.evaluate(() => [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Klasszikus').click()); await p.waitForTimeout(200);
  ok(/Imposztor-segítség/.test(await p.evaluate(() => document.body.innerText)), 'Klasszikus módban visszajön');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
