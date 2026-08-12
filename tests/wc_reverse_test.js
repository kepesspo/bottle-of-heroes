// v10.333 — Fordított kör: a banner és a könyvelés UGYANAZT mondja
//
// A TÜNET (Collect & Boom): a „Fordított kör" wildcard alatt a könyvelés
// megfordult — a bombás kapott pontot, a többiek ittak —, a banner viszont a
// régi állást mutatta: „Sere csapta fel a bombát! · ISZIK".
//
// AZ OK: a PlayScreen `onResult`-jában a csere kapuja a `winners`/`losers`
// tömbre szűrt. A LEGACY alak (`{correct, playerName, drinks, subtitle}`) egyiket
// sem viszi, tehát a feltétel hamis volt, és a banner változatlanul ment tovább.
// A könyvelés (`advance` / `advancePaired` / `advanceTeam` / `advanceLoverseny`)
// MIND kezeli a reverse-t — ezért csúszott szét a kettő.
//
// Ez nem egy játék hibája volt: 34 hívási hely (~15 játék) használja a legacy
// alakot, és mind ugyanígy kimaradt. Ezért van itt KÉT játék:
//   • `collect`  — a bejelentett eset, ez már a teljes alakot adja;
//   • `mitval`   — MARADT legacy alak, tehát az általánosított kaput méri.
//
// A FOGÓDZÓ a két állítás EGYEZÉSE, nem a konkrét oldal: aki a banneren nyertes,
// annak pontot kell kapnia és nem ihat, és fordítva. A javítás előtt a `collect`
// és a `mitval` blokk is pont ezen bukik.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'a', name:'Sere',  color:'#E07A5F', points:0, drinks:0 },
            { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
            { id:'c', name:'Vivi',  color:'#A78BFA', points:0, drinks:0 }];

// `fixRandom`: a Kviz osszekeveri a valaszokat, ezert kivulrol nem tudhato,
// melyik betu a helyes. `Math.random = 0.5` mellett a forrasbeli `a[0]` marad az
// „A" opcio — ugyanaz a fogodzo, amit a `quiz_test` hasznal. Csak a kviz-blokkban
// kapcsoljuk be: a wildcard sorsolasa is `Math.random`-ot hasznal, es a tobbi
// blokkban nem akarjuk befolyasolni.
async function open(b, effect, fixRandom) {
  const p = await b.newPage({ viewport: { width: 402, height: 1000 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}
    ${effect ? `window.__wildcardTestEffect=${JSON.stringify(effect)}; window.__wildcardTestDelay=400;` : ''}
    ${fixRandom ? 'Math.random = function(){ return 0.5; };' : ''}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

// PlayScreen mountolasa EGY jatekkal. FONTOS: a `modes` nelkul a `trackScores`
// hamis, a konyveles meg sem tortenik, es a Kovi gomb vegig letiltott marad —
// a meres ilyenkor csupa nullat ad (lasd CLAUDE.md v10.327 harness-buktato).
const mount = (p, gameId, wc) => p.evaluate(({ pl, gameId, wc }) => {
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  const root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
  document.body.appendChild(root);
  function H() {
    const [ps, setPs] = React.useState(pl);
    window.__players = ps;
    return React.createElement(PlayScreen, {
      go: () => {}, players: ps, setPlayers: setPs, selectedGames: [gameId], roomCode: null,
      gameMeta: { modes: wc ? ['points','drinks','wildcard'] : ['points','drinks'],
                  difficulty: 'easy', wildcardMin: 1, wildcardMax: 1 },
      setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {} });
  }
  ReactDOM.createRoot(root).render(React.createElement(H));
}, { pl: PL, gameId, wc });

// A banner ket sora: a „NYERTES(EK)" es az „ISZIK/ISZNAK" felirathoz tartozo
// neveket olvassuk ki. Felfele lepkedunk a felirattol, amig jatekos-nev nem
// kerul a szovegbe — egy fonel a nev a felirat testvere, tobbnel egy szinttel
// feljebb, teljes szelessegu sorban all.
const bannerSides = (p, names) => p.evaluate((names) => {
  const out = { win: [], lose: [], draw: [] };
  // A banner a PlayScreen faban ul (position:fixed, de nem portal) — a `#__p`-re
  // szurunk, kulonben az elrejtett `#root` szovege is beleszamitana.
  [...document.querySelectorAll('#__p span')].forEach(s => {
    const t = (s.textContent || '').trim().toLowerCase();
    const kind = /^nyertes(ek)?$/.test(t) ? 'win' : /^isz(ik|nak)$/.test(t) ? 'lose'
               : /^döntetlen$/.test(t) ? 'draw' : null;
    if (!kind) return;
    let el = s;
    for (let i = 0; i < 4 && el.parentElement; i++) {
      el = el.parentElement;
      const found = names.filter(n => (el.textContent || '').includes(n));
      if (found.length) { out[kind] = found; return; }
    }
  });
  return out;
}, names);

const players = p => p.evaluate(() => (window.__players || []).map(x => ({ n:x.name, pt:x.points, dr:x.drinks })));

const waitWc = async (p) => {
  for (let i = 0; i < 40; i++) {
    if (await p.evaluate(() => /Fordított kör/.test(document.body.innerText))) return true;
    await p.waitForTimeout(200);
  }
  return false;
};

// A banner megjeleneset EGY fogodzo jelzi mindharom blokkban: a „Nyertes(ek)" /
// „Iszik/Isznak" felirat. (A `textContent`-et nezzuk: a nagybetus alak csak
// `text-transform`, az `innerText` viszont a rejtett `#root`-ot is hozna.)
const hasBanner = p => p.evaluate(() =>
  [...document.querySelectorAll('#__p span')].some(s => /^(Nyertes(ek)?|Isz(ik|nak)|Döntetlen)$/.test((s.textContent||'').trim())));

// A racs mezoi `<div onClick>` elemek — nincs sajat `onclick` tulajdonsaguk
// (a React a gyokeren figyel), ezert a SZULO racsbol es a `cursor:pointer`-bol
// azonositjuk oket.
const driveCollect = async (p) => {
  for (let i = 0; i < 60; i++) {
    if (await hasBanner(p)) return true;
    await p.evaluate(() => {
      const cells = [...document.querySelectorAll('#__p div')].filter(d =>
        d.parentElement && getComputedStyle(d.parentElement).display === 'grid'
        && getComputedStyle(d).cursor === 'pointer');
      if (cells.length) cells[Math.floor(Math.random() * cells.length)].click();
    });
    await p.waitForTimeout(150);
  }
  return false;
};

// „Felfed & Indít", majd az A oldal. Az eredmeny 1,2 mp-cel a valasztas utan
// magatol elsul (`handleResult`), nincs kulon megerosito gomb.
const driveMitval = async (p) => {
  await p.evaluate(() => {
    const x = [...document.querySelectorAll('#__p button')].find(y => /Felfed & Indít/.test(y.textContent || ''));
    if (x) x.click();
  });
  await p.waitForTimeout(800);
  await p.evaluate(() => {
    const opts = [...document.querySelectorAll('#__p button')]
      .filter(y => (y.textContent || '').trim().length > 8 && y.getBoundingClientRect().height > 100);
    if (opts.length) opts[0].click();
  });
  for (let i = 0; i < 30; i++) {
    if (await hasBanner(p)) return true;
    await p.waitForTimeout(200);
  }
  return false;
};

// A Kovi gomb commitalja a kort (pendingCommit) — a konyveles ELOTTE meg nincs
// a players tombben.
// KVIZ: helyes valasz -> „Bankolom" -> egy korty kiosztasa -> „Mentés".
// Ez a `confirmGift` ag — VALODI konyveles (`onAdvance(drinkMap, {kihivo:1})`).
// ⚠️ A kviz elso valasza a forrasban az a[0], ezert azt a betut nyomjuk.
const driveQuiz = async (p) => {
  // A `QUIZ_DB` a komponens TORZSEBEN ul, tehat kivulrol nem lathato — a helyes
  // valasz viszont mindig az „A" opcio (a forrasban `a[0]`), ugyanaz a fogodzo,
  // amit a `quiz_test` is hasznal.
  const hit = await p.evaluate(() => {
    const btn = [...document.querySelectorAll('#__p button')]
      .find(x => /^A\n/.test(x.innerText || ''));
    if (!btn) return null;
    btn.click(); return (btn.innerText || '').replace('\n', ' ');
  });
  if (!hit) return false;
  await p.waitForTimeout(900);
  const bank = await p.evaluate(() => {
    const b = [...document.querySelectorAll('#__p button')].find(x => /Bankolom/.test(x.innerText || ''));
    if (!b) return false; b.click(); return true;
  });
  if (!bank) return false;
  await p.waitForTimeout(900);
  await p.evaluate(() => {
    const plus = [...document.querySelectorAll('#__p button[aria-label="Egy korttyal több"]')];
    if (plus[0]) plus[0].click();
  });
  await p.waitForTimeout(400);
  return p.evaluate(() => {
    const b = [...document.querySelectorAll('#__p button')].find(x => /Mentés/.test(x.innerText || ''));
    if (!b) return false; b.click(); return true;
  });
};

const commit = async (p) => {
  await p.evaluate(() => {
    const x = [...document.querySelectorAll('#__p button')].find(y => /Kövi/.test(y.textContent || ''));
    if (x && !x.disabled) x.click();
  });
  await p.waitForTimeout(1500);
};

// A kettot vetjuk ossze: aki a banneren nyertes, kapjon pontot es NE igyon.
function agree(sides, before, after, label) {
  const d = n => { const a = after.find(x => x.n === n), b = before.find(x => x.n === n);
                   return { pt: a.pt - b.pt, dr: a.dr - b.dr }; };
  ok(sides.win.length + sides.lose.length > 0, label + ': van kiolvasható oldal a banneren',
     JSON.stringify(sides));
  sides.win.forEach(n => ok(d(n).pt > 0 && d(n).dr === 0,
    `${label}: ${n} a banneren NYERTES → pontot kap, nem iszik`, JSON.stringify(d(n))));
  sides.lose.forEach(n => ok(d(n).dr > 0 && d(n).pt === 0,
    `${label}: ${n} a banneren ISZIK → kortyot kap, nem pontoz`, JSON.stringify(d(n))));
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const names = PL.map(x => x.name);

  // ── 1. Collect & Boom, FORDÍTOTT kör ──
  console.log('\n===== 1. COLLECT & BOOM — FORDITOTT KOR =====');
  let p = await open(b, 'reverse');
  await mount(p, 'collect', true);
  await p.waitForTimeout(1200);
  ok(await waitWc(p), 'a „Fordított kör" wildcard aktív');
  const before1 = await players(p);
  ok(await driveCollect(p), 'a kör lezárult (felrobbant a bomba)');
  await p.waitForTimeout(300);   // a banner 2600 ms utan osszecsukodik
  const s1 = await bannerSides(p, names);
  await commit(p);
  const after1 = await players(p);
  console.log('  banner:', JSON.stringify(s1), ' könyvelés:', JSON.stringify(after1));
  agree(s1, before1, after1, 'collect');
  // ...es a bombas TENYLEG atkerult a nyertes oldalra
  ok(s1.win.length === 1 && s1.lose.length === 2,
     'fordítva: a bombás EGYEDÜL nyer, a másik kettő iszik', JSON.stringify(s1));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 2. Collect & Boom wildcard NELKUL (kontroll) ──
  console.log('\n===== 2. COLLECT & BOOM — WILDCARD NELKUL (kontroll) =====');
  p = await open(b, null);
  await mount(p, 'collect', false);
  await p.waitForTimeout(1200);
  ok(!(await p.evaluate(() => /Fordított kör/.test(document.body.innerText))), 'nincs aktív wildcard');
  const before2 = await players(p);
  ok(await driveCollect(p), 'a kör lezárult');
  await p.waitForTimeout(300);
  const s2 = await bannerSides(p, names);
  await commit(p);
  const after2 = await players(p);
  console.log('  banner:', JSON.stringify(s2), ' könyvelés:', JSON.stringify(after2));
  agree(s2, before2, after2, 'collect/kontroll');
  ok(s2.lose.length === 1 && s2.win.length === 2,
     'normál kör: a bombás EGYEDÜL iszik, a másik kettő pontoz', JSON.stringify(s2));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 3. Mit választanál — MARADT legacy alak, az altalanositott kaput meri ──
  console.log('\n===== 3. MIT VALASZTANAL — LEGACY ALAK, FORDITOTT KOR =====');
  p = await open(b, 'reverse');
  await mount(p, 'mitval', true);
  await p.waitForTimeout(1200);
  ok(await waitWc(p), 'a „Fordított kör" wildcard aktív');
  const before3 = await players(p);
  ok(await driveMitval(p), 'a kör lezárult');
  await p.waitForTimeout(300);
  const s3 = await bannerSides(p, names);
  await commit(p);
  const after3 = await players(p);
  console.log('  banner:', JSON.stringify(s3), ' könyvelés:', JSON.stringify(after3));
  agree(s3, before3, after3, 'mitval');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 4. KVIZ ajandek-kiosztas, FORDITOTT kor (v10.354) ──
  // ⚠️ Ez volt a masik legacy alak VALODI konyvelessel: `confirmGift` kortyot
  // osztott ES pontot adott, a bannert viszont `playerName:null`-lal kuldte —
  // a konyveles megfordult, a banner nem.
  console.log('\n===== 4. KVIZ AJANDEK — FORDITOTT KOR =====');
  p = await open(b, 'reverse', true);
  await mount(p, 'quiz', true);
  await p.waitForTimeout(1400);
  ok(await waitWc(p), 'a „Fordított kör" wildcard aktív');
  const before4 = await players(p);
  ok(await driveQuiz(p), 'a kör lezárult (bankolás + korty kiosztása)');
  await p.waitForTimeout(400);
  const s4 = await bannerSides(p, names);
  await commit(p);
  const after4 = await players(p);
  console.log('  banner:', JSON.stringify(s4), ' könyvelés:', JSON.stringify(after4));
  agree(s4, before4, after4, 'quiz');
  ok(s4.win.length > 0 && s4.lose.length > 0,
     'a banner mindkét oldalt megnevezi (nem üres legacy alak)', JSON.stringify(s4));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 5. KVIZ ajandek wildcard NELKUL (kontroll) ──
  console.log('\n===== 5. KVIZ AJANDEK — WILDCARD NELKUL (kontroll) =====');
  p = await open(b, null, true);
  await mount(p, 'quiz', false);
  await p.waitForTimeout(1400);
  const before5 = await players(p);
  ok(await driveQuiz(p), 'a kör lezárult');
  await p.waitForTimeout(400);
  const s5 = await bannerSides(p, names);
  await commit(p);
  const after5 = await players(p);
  console.log('  banner:', JSON.stringify(s5), ' könyvelés:', JSON.stringify(after5));
  agree(s5, before5, after5, 'quiz/kontroll');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
