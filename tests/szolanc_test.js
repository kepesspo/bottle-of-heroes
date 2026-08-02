// v10.284 — Szólánc: "A" irány + hat logikai hiba
//
// Amit ellenőriz:
//   1. az ÁTADÁS és a VILLANTÁS lapja UGYANAZ a téglalap (méret ÉS pozíció) —
//      enélkül a „Kezdem" után ugrik a doboz
//   2. nincs többé bedrótozott sárga tábla (#F6C842) és nincs lakat
//   3. a lánc-sor TÖRDEL, nem csonkol — a régi tálca a 7. szinten 27 px-et adott
//      a szónak, miközben a „Debrecen" 58-at kért
//   4. a létra a valós szintszámot mutatja, nem fix 5 pöttyöt
//   5. nehéz fokozaton a lap a VALÓS kortyszámot írja ki, és egyezik a bannerrel
//      (eddig „iszik 1 kortyot" állt, miközben 3 ment el)
//   6. a többiek megkapják a pontot, amit a leírás ígér
//   7. a lánc partinként kevert — nem a lista első n szava
//   8. csali sosem lehet jövőbeli láncszem
//   9. a lánc 12 szónál ér véget, nem zsákutca, és MINDENKI kap +1 pontot
//  10. v10.285: EGY SZÍN = EGY TÉT — a lap színe és a kiosztott korty együtt
//      lép fokozatot (zöld 1 · sárga 2 · rózsa 3)
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

async function mount(p, n, diff) {
  await p.evaluate(({ n, diff }) => {
    const old = document.getElementById('__p'); if (old) old.remove();
    [...document.body.children].forEach(c => { if (c.id !== '__p') c.style.display = 'none'; });
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const nev = ['Sere', 'Kecsi', 'Luca', 'Tóth'].slice(0, n);
    function H() {
      const [players, setPlayers] = React.useState(nev.map((x, i) => ({ id: 'p' + i, name: x, color: '#5BA0DB', points: 0, drinks: 0 })));
      window.__players = players;
      return React.createElement(PlayScreen, {
        go: () => {}, players, setPlayers, selectedGames: ['szolánc'],
        roomCode: null, setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
        gameMeta: { modes: ['points'], difficulty: diff },
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  }, { n, diff });
  await p.waitForTimeout(2600);
  await p.evaluate(() => { const pop = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '9998'); if (pop) pop.click(); });
  await p.waitForTimeout(500);
}

// A 288 px-es lap geometriaja a 402-es rendszerben (a teszt 1:1-ben fut).
const lapRect = p => p.evaluate(() => {
  const R = document.getElementById('__p');
  const k = [...R.querySelectorAll('div')].find(d => Math.round(d.getBoundingClientRect().height) === 288);
  if (!k) return null;
  const r = k.getBoundingClientRect();
  return { m: Math.round(r.height), y: Math.round(r.top), bg: getComputedStyle(k).backgroundColor };
});

const indit = async p => {
  await p.evaluate(() => { const b = [...document.getElementById('__p').querySelectorAll('button')].find(x => /Kezdem/.test(x.innerText || '')); b && b.click(); });
};

// Gyujti a felvillano szavakat, majd visszater a recall-fazisban lathato raccsal.
//
// A szot NEM a betumeretbol ismerjuk fel: az atadas-lapon a jatekos NEVE is
// 26 px / 900, tehat az elso valtozat a neveket is szonak nezte, es ettol a
// lanc hamis lett (ez buktatta a 3. es az 5-6. szakaszt).
// Helyette: csak a 288 px-es hofok-lapon belul, a `letterSpacing:-0.03em`
// alapjan — ez a jelolo csak a villano szon van.
const allapot = p => p.evaluate(() => {
  const R = document.getElementById('__p');
  const gombok = [...R.querySelectorAll('button')];
  if (gombok.some(x => /Kezdem/.test(x.innerText || ''))) return { fazis: 'ready', szo: null, racs: [] };
  const lap = [...R.querySelectorAll('div')].find(d => Math.round(d.getBoundingClientRect().height) === 288);
  if (lap) {
    const d = [...lap.querySelectorAll('div')].find(x => x.style && x.style.letterSpacing === '-0.03em');
    return { fazis: 'show', szo: d ? (d.innerText || '').trim() : null, racs: [] };
  }
  // A racs gombjait a sajat lekerekitesuk azonositja (17px). Nevre szurni nem
  // eleg: az info gomb szovege "i", tehat csalinak szamitana — es a hibas
  // koppintas helyett az info-ablakot nyitna meg.
  const racs = gombok.filter(x => x.style && x.style.borderRadius === '17px')
                     .map(x => (x.innerText || '').trim());
  return { fazis: racs.length >= 4 ? 'recall' : 'egyeb', szo: null, racs };
});

async function korLejatszas(p, hossz) {
  const lanc = [];
  const hatarido = Date.now() + hossz * 1600 + 9000;
  let racs = [];
  while (Date.now() < hatarido) {
    const st = await allapot(p);
    if (st.szo && lanc[lanc.length - 1] !== st.szo) lanc.push(st.szo);
    if (st.fazis === 'recall') { racs = st.racs; break; }
    await p.waitForTimeout(110);
  }
  return { lanc, racs };
}

const koppint = async (p, szavak) => {
  for (const w of szavak) {
    await p.evaluate((w) => {
      const R = document.getElementById('__p');
      const b = [...R.querySelectorAll('button')].find(x => (x.innerText || '').trim() === w && !x.disabled);
      b && b.click();
    }, w);
    await p.waitForTimeout(150);
  }
};

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: 402, height: 874 } });
  const p = await ctx.newPage();
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.route('**/*', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.goto('file://' + path.join(ROOT, 'index.html'));
  await p.waitForTimeout(1800);

  console.log('\n===== 1. AZ ÁTADÁS ÉS A VILLANTÁS UGYANAZ A TÉGLALAP =====');
  await mount(p, 4, 'easy');
  const atadas = await lapRect(p);
  ok(atadas && atadas.m === 288, 'az átadás lapja 288 px', atadas && atadas.m);
  await indit(p);
  await p.waitForTimeout(500);
  const villantas = await lapRect(p);
  ok(villantas && villantas.m === 288, 'a villantás lapja is 288 px', villantas && villantas.m);
  ok(atadas && villantas && atadas.y === villantas.y,
     'és UGYANOTT is van — a „Kezdem" után nem ugrik a doboz',
     atadas && villantas ? `y=${atadas.y} vs y=${villantas.y}` : 'nincs adat');
  ok(atadas && villantas && atadas.bg !== villantas.bg,
     'de a színük különbözik: az átadás fehér, a villantás hőfok-lap',
     atadas && villantas ? `${atadas.bg} → ${villantas.bg}` : '');

  console.log('\n===== 2. NINCS SÁRGA TÁBLA, NINCS LAKAT =====');
  const tabla = await p.evaluate(() => {
    const R = document.getElementById('__p');
    return [...R.querySelectorAll('div')].filter(d => getComputedStyle(d).backgroundColor === 'rgb(246, 200, 66)').length;
  });
  ok(tabla === 0, 'a bedrótozott #F6C842 tábla eltűnt', tabla + ' db');
  const forras = await p.evaluate(() => document.documentElement.innerHTML);
  ok(!/SzolancWrap/.test(forras), 'a SzolancWrap komponens sincs többé');
  const pasztell = ['#C9E8D2', '#F5E0AC', '#F2C4C4'].every(h => forras.includes(h));
  ok(pasztell, 'a három hőfok-pasztell a Szerencsekerék palettájából áll');

  console.log('\n===== 3. A LÁNC-SOR TÖRDEL, NEM CSONKOL =====');
  // Felmegyunk a 6. szintig, ahol a regi talca 47 px-es dobozokat adott.
  await mount(p, 4, 'easy');
  let utolsoRacs = null;
  for (let szint = 2; szint <= 6; szint++) {
    await indit(p);
    utolsoRacs = await korLejatszas(p, szint);
    if (szint === 6) break;
    await koppint(p, utolsoRacs.lanc);
    await p.waitForTimeout(1700);
  }
  ok(utolsoRacs.lanc.length === 6, 'a 6. szinten hat szó villant fel', utolsoRacs.lanc.length);
  // A 6. szinten leteszunk otot, hogy a sor tobb sorba tordeljon.
  await koppint(p, utolsoRacs.lanc.slice(0, 5));
  const sor = await p.evaluate(() => {
    const R = document.getElementById('__p');
    // A pirula `inline-flex`-kent van megadva, de flex-elemkent BLOKKOSODIK,
    // tehat a szamitott erteke `flex` — az `inline-flex`-re szuro valtozat
    // egyet sem talalt. A jelveny es a "meg N" viszont `block`, igy elvalnak.
    const pirulak = [...R.querySelectorAll('span')].filter(s => {
      const st = getComputedStyle(s);
      return st.borderRadius === '999px' && st.display === 'flex';
    });
    const sorok = new Set(pirulak.map(s => Math.round(s.getBoundingClientRect().top))).size;
    const csonk = pirulak.filter(s => s.scrollWidth > s.clientWidth + 1).length;
    return { db: pirulak.length, sorok, csonk,
             szavak: pirulak.map(s => (s.innerText || '').replace(/\s+/g, ' ').trim()) };
  });
  ok(sor.db === 5, 'öt szó került a lánc-sorba', sor.db + ' db');
  ok(sor.sorok >= 2, 'és több sorba tördel, ahelyett hogy összenyomná', sor.sorok + ' sor');
  ok(sor.csonk === 0, 'egyetlen szó sincs csonkolva', sor.csonk + ' csonkolt');

  console.log('\n===== 4. A LÉTRA A VALÓS SZINTSZÁMOT MUTATJA =====');
  await koppint(p, utolsoRacs.lanc.slice(5));
  await p.waitForTimeout(1800);
  const letra = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const sav = [...R.querySelectorAll('div')].filter(d => d.style && d.style.height === '7px' && d.style.borderRadius === '4px');
    const kesz = sav.filter(d => getComputedStyle(d).backgroundColor !== 'rgba(26, 42, 74, 0.13)').length;
    return { db: sav.length, kesz };
  });
  ok(letra.db > 5, 'a létra nem fix 5 szakaszból áll', letra.db + ' szakasz');
  ok(letra.kesz === 6, 'és a 7. szinten hat szakasz aktív (nem fagy be ötnél)', letra.kesz);

  console.log('\n===== 5-6. VALÓS KORTYSZÁM + A TÖBBIEK PONTJA (nehéz, ×3) =====');
  await mount(p, 4, 'hard');
  const korong = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const d = [...R.querySelectorAll('div')].find(x => x.offsetWidth === 54 && /korty/i.test(x.innerText || ''));
    return d ? (d.innerText || '').replace(/\s+/g, ' ').trim() : null;
  });
  await indit(p);
  const k2 = await korLejatszas(p, 2);
  ok(k2.lanc.length === 2, 'két szó villant fel a 2. szinten', k2.lanc.join(' → '));
  const rossz = k2.racs.find(w => w !== k2.lanc[0]);
  await koppint(p, [rossz]);
  await p.waitForTimeout(1400);
  const bukas = await p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));
  ok(/iszik 3 kortyot/.test(bukas), 'a lap a VALÓS kortyszámot írja (nem bedrótozott 1-et)',
     (bukas.match(/iszik \d+ kortyot/) || ['nincs'])[0]);
  ok(korong === '3–9 KORTY', 'a korong a valós tartományt mutatja (stake [1,3] × 3)', korong);
  ok(/mindenki más \+1 pont/.test(bukas), 'kiírja a többiek pontját is');

  await p.evaluate(() => { const b = [...document.getElementById('__p').querySelectorAll('button')].find(x => /Kövi/.test(x.innerText || '')); b && b.click(); });
  await p.waitForTimeout(900);
  const allas = await p.evaluate(() => (window.__players || []).map(x => `${x.name}:${x.drinks}k/${x.points}p`).join(', '));
  const ivo = await p.evaluate(() => (window.__players || []).filter(x => x.drinks > 0));
  const pontosak = await p.evaluate(() => (window.__players || []).filter(x => x.points > 0).length);
  ok(ivo.length === 1 && ivo[0].drinks === 3, 'a vesztes tényleg 3 kortyot kapott', allas);
  ok(pontosak === 3, 'és a másik három pontot kapott', pontosak + ' játékos');

  console.log('\n===== 7-8. KEVERT LÁNC, ÉS A CSALI NEM JÖVŐBELI LÁNCSZEM =====');
  const elsok = new Set();
  let atfedes = 0, mintak = 0;
  for (let m = 0; m < 4; m++) {
    await mount(p, 4, 'easy');
    await indit(p);
    const { lanc, racs } = await korLejatszas(p, 2);
    if (lanc[0]) elsok.add(lanc[0]);
    const csalik = racs.filter(w => !lanc.includes(w));
    if (m === 0) {
      ok(racs.length === 5, 'a rács 2 láncszó + 3 csali', racs.length + ' gomb');
      ok(csalik.length === 3, 'három csali kerül a rácsba', csalik.length);
    }
    // Vigyuk fel a lancot ket szinttel, es nezzuk meg, hogy a korabbi csalik
    // kozul bekerult-e barmelyik a lancba.
    await koppint(p, lanc);
    await p.waitForTimeout(1700);
    await indit(p);
    const k3 = await korLejatszas(p, 3);
    await koppint(p, k3.lanc);
    await p.waitForTimeout(1700);
    await indit(p);
    const k4 = await korLejatszas(p, 4);
    mintak++;
    if (k4.lanc.some(w => csalik.includes(w))) atfedes++;
  }
  ok(elsok.size > 1, 'a lánc partinként más — nem a lista első n szava', elsok.size + ' különböző nyitószó/4 indítás');
  ok(atfedes === 0, 'és a csalik közül egy sem lett később láncszem', atfedes + ' átfedés / ' + mintak + ' minta');

  console.log('\n===== 9. A LÁNC 12 SZÓNÁL ÉR VÉGET, ÉS MINDENKI PONTOT KAP =====');
  await mount(p, 4, 'easy');
  let hossz = 2, vege = false;
  for (let lvl = 0; lvl < 16 && !vege; lvl++) {
    await indit(p);
    const { lanc } = await korLejatszas(p, hossz);
    if (!lanc.length) break;
    await koppint(p, lanc);
    await p.waitForTimeout(1900);
    vege = await p.evaluate(() => /Megvan mind a \d+/.test(document.getElementById('__p').innerText || ''));
    hossz++;
  }
  ok(vege && hossz - 1 === 12, 'a lánc pontosan 12 szónál zárul le', hossz - 1 + ' szó');
  const nyeroLap = await p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));
  ok(/mindenki \+1 pont/.test(nyeroLap), 'a nyerő lap kiírja, hogy mindenki pontot kap');
  const kovi = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const b = [...R.querySelectorAll('button')].find(x => /Kövi/.test(x.innerText || ''));
    return b ? getComputedStyle(b).backgroundColor : null;
  });
  ok(kovi && kovi !== 'rgba(0, 0, 0, 0)' && !/246, 241, 230/.test(kovi),
     'és a Kövi gomb AKTÍV (eddig holtan maradt, mert nem volt pendingCommit)', kovi);
  await p.evaluate(() => { const x = [...document.getElementById('__p').querySelectorAll('button')].find(y => /Kövi/.test(y.innerText || '')); x && x.click(); });
  await p.waitForTimeout(900);
  const jackpot = await p.evaluate(() => (window.__players || []).map(x => `${x.name}:${x.points}p/${x.drinks}k`).join(', '));
  const mindPontos = await p.evaluate(() => (window.__players || []).every(x => x.points === 1 && x.drinks === 0));
  ok(mindPontos, 'és mind a négyen tényleg megkapták a pontot, korty nélkül', jackpot);

  console.log('\n===== 10. EGY SZÍN = EGY TÉT =====');
  // Minden fokozaton felmegyunk a hatarig, elrontjuk, es megnezzuk, hogy a lap
  // szine ES a ténylegesen kiosztott korty egyutt lepett-e fokozatot.
  const FOKOZAT = [
    { szint: 2, szin: 'rgb(201, 232, 210)', korty: 1, nev: 'zöld' },
    { szint: 5, szin: 'rgb(245, 224, 172)', korty: 2, nev: 'sárga' },
    { szint: 8, szin: 'rgb(242, 196, 196)', korty: 3, nev: 'rózsa' },
  ];
  for (const f of FOKOZAT) {
    await mount(p, 4, 'easy');
    let kor = null;
    for (let lvl = 2; lvl <= f.szint; lvl++) {
      await indit(p);
      kor = await korLejatszas(p, lvl);
      if (lvl === f.szint) break;
      await koppint(p, kor.lanc);
      await p.waitForTimeout(1800);
    }
    const lapSzin = await p.evaluate(() => {
      const R = document.getElementById('__p');
      const k = [...R.querySelectorAll('div')].find(d => d.style && d.style.borderRadius === '26px' && d.style.padding === '16px');
      return k ? getComputedStyle(k).backgroundColor : null;
    });
    ok(lapSzin === f.szin, `${f.szint} szónál a lap ${f.nev}`, lapSzin);
    // szandekosan rossz koppintas: olyan racs-szo, ami nem a kovetkezo helyes
    const rosszSzo = kor.racs.find(w => w !== kor.lanc[0]);
    await koppint(p, [rosszSzo]);
    await p.waitForTimeout(1500);
    const lap = await p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));
    ok(new RegExp(`iszik ${f.korty} kortyot`).test(lap),
       `és a lap ${f.korty} kortyot ír`, (lap.match(/iszik \d+ kortyot/) || ['nincs'])[0]);
    await p.evaluate(() => { const b = [...document.getElementById('__p').querySelectorAll('button')].find(x => /Kövi/.test(x.innerText || '')); b && b.click(); });
    await p.waitForTimeout(900);
    const kapott = await p.evaluate(() => Math.max(0, ...(window.__players || []).map(x => x.drinks)));
    ok(kapott === f.korty, `és a játékos tényleg ${f.korty} kortyot kapott`, kapott);
  }

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})();
