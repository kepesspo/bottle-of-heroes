// v10.279 — Én még soha: kevert pakli, kapcsoló, közös korty-osztó sor
//
// Amit ellenőriz:
//   1. a pakli PARTINKÉNT meg van keverve — eddig `SOHANEM_CARDS[gameIdx % 207]`
//      volt, tehát minden parti ugyanazzal a lappal indult, és egy 20-40 játékos
//      buliban a 207-ből csak az első ~40 lap került valaha elő
//   2. a sorokban a BÜNTETÉSNÉL használt léptető van, de 1-es plafonnal:
//      a `+` az 1. korty után letiltott (igaz/hamis kérdés)
//   3. a záró gomb helye NEM függ a játékosszámtól — eddig 10 főnél 940 px-nél
//      volt egy 874 px-es képernyőn, tehát kicsúszott
//   4. a banner kiírja a számot, ha mindenki ugyanannyit kap
//   5. nincs többé duplán feltett kérdés és fűszer-csík
//   6. v10.281: kiosztás után a gomb eltűnik és a sorok lezárnak, és a sor
//      SZÉLESSÉGE is azonos a Büntetés-modaléval (296 px)
//   7. v10.282: HŐFOK-LAP — a lap színe a fűszerszint (zöld / narancs / vörös),
//      és a három szín FIX, nem témafüggő; a lista címe „Ki iszik?", középen
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

const DRINK_SOR = 48;   // egy korty-oszto sor magassaga
const NEVEK = ['Sere','Kecsi','Luca','Tóth','Márk','Dani','Vivi','Bence','Zsolt','Anna'];

async function mount(p, n) {
  await p.evaluate((n) => {
    const old = document.getElementById('__p'); if (old) old.remove();
    [...document.body.children].forEach(c => { if (c.id !== '__p') c.style.display = 'none'; });
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const nev = ['Sere','Kecsi','Luca','Tóth','Márk','Dani','Vivi','Bence','Zsolt','Anna'].slice(0, n);
    function H() {
      const [players, setPlayers] = React.useState(nev.map((x,i)=>({ id:'p'+i, name:x, color:'#5BA0DB', points:0, drinks:0 })));
      window.__players = players;
      return React.createElement(PlayScreen, { go:()=>{}, players, setPlayers, selectedGames:['sohanem'],
        roomCode:null, setGameMeta:()=>{}, setScoreHistory:()=>{}, setLastGameRound:()=>{},
        gameMeta:{ modes:['points'], difficulty:'easy' } });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  }, n);
  await p.waitForTimeout(2600);
  await p.evaluate(() => { const pop=[...document.querySelectorAll('div')].find(d=>d.style&&d.style.zIndex==='9998'); if(pop) pop.click(); });
  await p.waitForTimeout(500);
}

const olvas = p => p.evaluate(() => {
  const R = document.getElementById('__p');
  const btn = [...R.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik|iszik ·/.test(x.innerText||''));
  const r = btn ? btn.getBoundingClientRect() : null;
  const lista = [...R.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto' && d.style.maxHeight);
  const sorok = lista ? [...lista.children] : [];
  const lr = lista ? lista.getBoundingClientRect() : null;
  const teljes = lr ? sorok.filter(s => { const b = s.getBoundingClientRect();
    return b.top >= lr.top - 0.5 && b.bottom <= lr.bottom + 0.5; }).length : 0;
  const txt = (R.innerText||'').replace(/\s+/g,' ');
  const lap = (txt.match(/(\d+)\/207/)||[])[1];
  const allitas = (txt.match(/Én még soha nem… ([^0-9]{5,90})/)||[])[1];
  return {
    gombAlja: r ? Math.round(r.bottom) : null, ablak: window.innerHeight,
    gombLathato: r ? (r.bottom <= window.innerHeight) : null,
    gombSzoveg: btn ? btn.innerText.trim() : null,
    sorDb: sorok.length, teljesenLatszik: teljes,
    listaMagassag: lr ? Math.round(lr.height) : null,
    sorMagassag: sorok[0] ? Math.round(sorok[0].getBoundingClientRect().height) : null,
    lap, allitas: (allitas||'').trim(),
    szoveg: txt.slice(0, 220),
  };
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);

  console.log('\n===== 1. A PAKLI MEG VAN KEVERVE =====');
  const latott = [];
  for (let i = 0; i < 4; i++) { await mount(p, 4); latott.push((await olvas(p)).allitas); }
  const kulonbozo = new Set(latott.filter(Boolean)).size;
  ok(latott.every(Boolean), 'minden indításnál van állítás', latott.map(s=>s.slice(0,22)).join(' | '));
  ok(kulonbozo > 1, 'NEM mindig ugyanaz a lap jön (eddig minden parti 01/207-tel indult)',
     kulonbozo + ' különböző / 4 indítás');
  // A kijelzo a KEVERT pakliban elfoglalt helyet mutatja, tehat az elso lap 01.
  ok((await olvas(p)).lap === '01', 'a számláló az első lapnál 01/207-et mutat', (await olvas(p)).lap);

  console.log('\n===== 2. A BÜNTETÉS LÉPTETŐJE, 1-ES PLAFONNAL =====');
  await mount(p, 4);
  const elotte = await olvas(p);
  ok(elotte.sorMagassag === 48, 'a sor 48 px — ugyanaz, mint a Büntetés-modalban', elotte.sorMagassag + ' px');
  const lepteto = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const lista = [...R.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto' && d.style.maxHeight);
    return lista ? [...lista.querySelectorAll('button')].filter(x => /^[−+]$/.test((x.textContent||'').trim())).length : -1;
  });
  ok(lepteto === 8, 'minden soron ott a − és a + (4 játékos)', lepteto + ' gomb');
  ok(!/NEM|IGEN/.test(elotte.szoveg), 'NINCS kapcsoló — a büntetésnél használt felület megy',
     elotte.szoveg.slice(0, 50));

  // `+` gomb egy soron, n-szer
  const plusz = async (nev, n) => p.evaluate(({nev, n}) => {
    const R = document.getElementById('__p');
    const lista = [...R.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto' && d.style.maxHeight);
    const sor = [...lista.children].find(s => (s.innerText||'').includes(nev));
    const b = sor && [...sor.querySelectorAll('button')].find(x => (x.textContent||'').trim() === '+');
    for (let i = 0; i < n; i++) if (b) b.click();
  }, {nev, n});
  const minusz = async (nev) => p.evaluate((nev) => {
    const R = document.getElementById('__p');
    const lista = [...R.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto' && d.style.maxHeight);
    const sor = [...lista.children].find(s => (s.innerText||'').includes(nev));
    const b = sor && [...sor.querySelectorAll('button')].find(x => (x.textContent||'').trim() === '−');
    if (b) b.click();
  }, nev);

  await plusz('Kecsi', 1); await p.waitForTimeout(300);
  ok((await olvas(p)).gombSzoveg === '1 iszik · 1 korty', 'egy koppintás 1 kortyot ad', (await olvas(p)).gombSzoveg);
  // EZ A LENYEG: tovabbi koppintasok NEM emelik 1 fole
  await plusz('Kecsi', 4); await p.waitForTimeout(300);
  ok((await olvas(p)).gombSzoveg === '1 iszik · 1 korty',
     'további 4 koppintás sem visz 1 fölé — a plafon 1', (await olvas(p)).gombSzoveg);
  const tiltva = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const lista = [...R.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto' && d.style.maxHeight);
    const sor = [...lista.children].find(s => (s.innerText||'').includes('Kecsi'));
    const b = [...sor.querySelectorAll('button')].find(x => (x.textContent||'').trim() === '+');
    return b ? b.disabled : null;
  });
  ok(tiltva === true, 'és a + gomb láthatóan letiltott a plafonon');
  // v10.280b: a plafon GYORS koppintasnal is tart. A `disabled` es a render-beli
  // orzes ilyenkor nem eleg: harom koppintas egy React-kotegbe esik, ahol a gomb
  // meg nincs letiltva. Ezert a plafon az allapotfrissitoben dol el.
  await mount(p, 4);
  await plusz('Kecsi', 3);   // EGY kotegben, varakozas nelkul
  await plusz('Tóth', 1);
  await p.waitForTimeout(400);
  ok((await olvas(p)).gombSzoveg === '2 iszik · 2 korty',
     'gyors, egymás utáni koppintás sem lépi túl a plafont', (await olvas(p)).gombSzoveg);
  // itt Kecsi=1 es Tóth=1 all a fenti kotegelt teszt utan
  await minusz('Kecsi'); await p.waitForTimeout(300);
  ok((await olvas(p)).gombSzoveg === '1 iszik · 1 korty', 'a − visszavesz', (await olvas(p)).gombSzoveg);
  await minusz('Tóth'); await p.waitForTimeout(300);
  ok((await olvas(p)).gombSzoveg === 'Senki sem iszik', 'nulláról már nem megy lejjebb', (await olvas(p)).gombSzoveg);

  console.log('\n===== 3. A ZÁRÓ GOMB HELYE FÜGGETLEN A LÉTSZÁMTÓL =====');
  const poz = {};
  for (const n of [4, 6, 10]) { await mount(p, n); const r = await olvas(p); poz[n] = r; }
  ok(poz[10].teljesenLatszik === 5, '10 játékosnál is csak 5 sor látszik (a többi görgethető)',
     poz[10].teljesenLatszik + ' sor');
  ok(poz[10].listaMagassag === 272, 'a lista 272 px — ugyanaz a korlát, mint a modalban', poz[10].listaMagassag + ' px');
  // 4 fonel a lista MEG NEM eri el a plafont (4 sor = 216 px), tehat ott
  // jogosan rovidebb — nem paddingoljuk fel uresen. Az osszehasonlithato eset a
  // 6 es a 10 fo: mindketto a 272-es plafonon ul, tehat a gombnak egy helyen
  // kell lennie. (Par px elteres maradhat, mert a v10.280 ota a lap a szoveg
  // hosszahoz igazodik — de az egy sornal jóval kisebb, mig a regi valtozatban
  // 6 -> 10 fo 208 px-et jelentett.)
  ok(poz[4].listaMagassag < 272, '4 játékosnál a lista rövidebb — nem tömjük ki üresen',
     poz[4].listaMagassag + ' px');
  const elteres = Math.abs(poz[6].gombAlja - poz[10].gombAlja);
  ok(elteres < DRINK_SOR, 'a gomb helye nem a létszámtól függ (6 vs 10 fő, mindkettő a plafonon)',
     `${poz[6].gombAlja} vs ${poz[10].gombAlja} — ${elteres} px eltérés, egy sor ${DRINK_SOR} px`);
  ok(poz[10].gombLathato, '10 játékosnál is a képernyőn van (eddig 940 / 874 volt)',
     poz[10].gombAlja + ' / ' + poz[10].ablak);

  console.log('\n===== 4. A BANNER KIÍRJA A SZÁMOT AZONOS ÖSSZEGNÉL =====');
  await mount(p, 4);
  await plusz('Kecsi', 1); await plusz('Luca', 1); await p.waitForTimeout(300);
  await p.evaluate(() => {
    const R = document.getElementById('__p');
    const btn = [...R.querySelectorAll('button')].find(x => /iszik ·/.test(x.innerText||''));
    if (btn) btn.click();
  });
  await p.waitForTimeout(900);
  const banner = await p.evaluate(() => {
    const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250');
    return el ? (el.innerText||'').replace(/\s+/g,' ').trim() : '';
  });
  ok(/1 KORTY/i.test(banner), 'mindenki 1-et kap → a banner „1 KORTY"-ot ír', (banner.match(/\d+ KORTY/i)||['nincs'])[0]);
  ok(/Kecsi/.test(banner) && /Luca/.test(banner), 'és mindkét név szerepel');
  // A korty a pendingCommit-ben ul, es a KÖVI gombra kerul fel — ez a v10.274
  // ota igy mukodik minden jateknal, nem ennek a jateknak a sajatja.
  const azonnal = await p.evaluate(() => window.__players.map(x => x.drinks).join(','));
  ok(azonnal === '0,0,0,0', 'a korty még a pendingCommit-ben ül (Kövire vár)', azonnal);
  await p.evaluate(() => {
    const R = document.getElementById('__p');
    const b2 = [...R.querySelectorAll('button')].find(x => /Kövi/i.test(x.innerText||''));
    if (b2) b2.click();
  });
  await p.waitForTimeout(2200);
  const st = await p.evaluate(() => window.__players.map(x => x.name + ':' + x.drinks).join(','));
  ok(st === 'Sere:0,Kecsi:1,Luca:1,Tóth:0', 'Kövi után a korty pontosan rákerült', st);

  console.log('\n===== 5. NINCS DUPLÁN FELTETT KÉRDÉS, NINCS FŰSZER-CSÍK =====');
  await mount(p, 4);
  const r5 = await olvas(p);
  ok(!/igaz rád\?/i.test(r5.szoveg), 'a képernyő teteje nem kérdez ugyanazt, amit a kártya',
     r5.szoveg.slice(0, 60));
  ok(!/Kire igaz\?/i.test(r5.szoveg), 'a régi „Kire igaz?" címke sincs többé');
  ok(/Olvasd fel/.test(r5.szoveg), 'helyette a kör feladatát mondja');
  const csik = await p.evaluate(() => {
    const R = document.getElementById('__p');
    return [...R.querySelectorAll('div')].filter(d => d.style && d.style.width === '20px' && d.style.height === '6px').length;
  });
  ok(csik === 0, 'a fűszer-csík eltűnt (a jelvény már kiírja a szintet)', csik + ' db');
  // v10.280: a harom elforgatott hatso lap kikerult — EGY tiszta hos-elem maradt
  const forgatott = await p.evaluate(() => {
    const R = document.getElementById('__p');
    return [...R.querySelectorAll('div')].filter(d => d.style && /rotate/.test(d.style.transform||'')).length;
  });
  ok(forgatott === 0, 'nincs több elforgatott hátsó lap — egy tiszta felület maradt', forgatott + ' db');

  console.log('\n===== 6. v10.281: A GOMB ELTŰNIK, ÉS AZONOS A SZÉLESSÉG =====');
  await mount(p, 4);
  const szel = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const lista = [...R.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto' && d.style.maxHeight);
    return Math.round(lista.getBoundingClientRect().width);
  });
  // A modal kartyaja 340 px, 22 px oldalpaddinggal -> 296 px tartalom (merve).
  ok(szel === 296, 'a lista 296 px — pont annyi, mint a Büntetés-modal tartalma', szel + ' px');
  await plusz('Kecsi', 1); await p.waitForTimeout(300);
  ok((await olvas(p)).gombSzoveg === '1 iszik · 1 korty', 'a gomb kiosztás előtt ott van');
  await p.evaluate(() => {
    const R = document.getElementById('__p');
    const b2 = [...R.querySelectorAll('button')].find(x => /iszik ·/.test(x.innerText||''));
    if (b2) b2.click();
  });
  await p.waitForTimeout(700);
  const utana = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const b2 = [...R.querySelectorAll('button')].find(x => /iszik ·|korty kiosztva|Senki sem iszik/.test(x.innerText||''));
    const lista = [...R.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto' && d.style.maxHeight);
    return { gomb: b2 ? b2.innerText.trim() : null,
             sorokZarva: lista ? getComputedStyle(lista).pointerEvents === 'none' : null,
             szoveg: (R.innerText||'').replace(/\s+/g,' ') };
  });
  ok(utana.gomb === null, 'kiosztás után a gomb eltűnik', utana.gomb === null ? 'nincs gomb' : utana.gomb);
  ok(utana.sorokZarva === true, 'és a sorok lezárnak (a módosítás úgyis nem számítana)');
  ok(/jöhet a Kövi/.test(utana.szoveg), 'helyette egy halk visszaigazolás áll ott',
     (utana.szoveg.match(/\d+ korty kiosztva — jöhet a Kövi/)||['nincs'])[0]);

  console.log('\n===== 7. v10.283: HŐFOK-LAP (halvány lap + telített jelvény) =====');
  // Tobb inditast probalunk, amig mindharom szint elojon (a pakli kevert).
  // A lap hattere a Szerencsekerek egy-egy pasztellje (WHEEL_TONES), a jelveny
  // ugyanaz telitve — ezert ket kulon szint ellenorzunk szintenkent.
  const HOFOK = {
    'ALAP':    { lap: 'rgb(201, 232, 210)', jelveny: 'rgb(79, 169, 127)' },
    'KÖZEPES': { lap: 'rgb(245, 224, 172)', jelveny: 'rgb(214, 154, 46)' },
    'VAD':     { lap: 'rgb(242, 196, 196)', jelveny: 'rgb(212, 106, 106)' },
  };
  const LAPOK = Object.values(HOFOK).map(x => x.lap);
  const hofokLatott = {};
  for (let i = 0; i < 16 && Object.keys(hofokLatott).length < 3; i++) {
    await mount(p, 4);
    const info = await p.evaluate((LAPOK) => {
      const R = document.getElementById('__p');
      const kartya = [...R.querySelectorAll('div')]
        .find(d => d.style && d.style.borderRadius === '26px' && LAPOK.includes(getComputedStyle(d).backgroundColor));
      if (!kartya) return null;
      const t = (kartya.innerText || '').replace(/\s+/g, ' ');
      const lv = (t.match(/ALAP|KÖZEPES|VAD/) || [])[0];
      const jel = [...kartya.querySelectorAll('span')].find(s => /ALAP|KÖZEPES|VAD/.test(s.textContent || ''));
      const cim = [...R.querySelectorAll('div')].find(d => (d.textContent || '').trim() === 'Ki iszik?');
      return { lv, lap: getComputedStyle(kartya).backgroundColor,
               tinta: getComputedStyle(kartya).color,
               perem: getComputedStyle(kartya).boxShadow,
               jelveny: jel ? getComputedStyle(jel).backgroundColor : null,
               jelvenyTinta: jel ? getComputedStyle(jel).color : null,
               cimVan: !!cim, cimIgazitas: cim ? getComputedStyle(cim).textAlign : null };
    }, LAPOK);
    if (info && info.lv && !hofokLatott[info.lv]) hofokLatott[info.lv] = info;
  }
  ok(Object.keys(hofokLatott).length === 3, 'mindhárom fűszerszint előjött', Object.keys(hofokLatott).join(', '));
  for (const [lv, vart] of Object.entries(HOFOK)) {
    const g = hofokLatott[lv];
    if (!g) { ok(false, `${lv}: nem jött elő`); continue; }
    ok(g.lap === vart.lap, `${lv}: a lap a kerék pasztellje`, g.lap);
    ok(g.jelveny === vart.jelveny, `${lv}: a jelvény ugyanaz telítve`, g.jelveny);
    // A KOZEPES lap (#F5E0AC) az alapertelmezett meleg temaban majdnem
    // pontosan a hatter szine — perem nelkul beleolvad.
    ok(/inset/.test(g.perem || ''), `${lv}: van hajszálvékony perem (különben beleolvad)`,
       (g.perem || '').replace(/,\s*rgba\(20, 30, 50[^)]*\)[^,]*$/, '').slice(0, 60));
  }
  const barmi = Object.values(hofokLatott)[0];
  // Pasztellen a feher olvashatatlan, a T.ink viszont sotet temaban vilagos —
  // ezert a tinta is FIX sotet.
  ok(barmi && barmi.tinta === 'rgb(20, 32, 47)', 'a lap szövege fix sötét (nem T.ink)', barmi && barmi.tinta);
  ok(barmi && barmi.jelvenyTinta === 'rgb(255, 255, 255)', 'a jelvény felirata fehér', barmi && barmi.jelvenyTinta);
  ok(barmi && barmi.cimVan, 'a lista címe „Ki iszik?" (nem „Kire igaz?")');
  ok(barmi && barmi.cimIgazitas === 'center', 'és középre igazított', barmi && barmi.cimIgazitas);
  // A hat szin FIX: a T.* tokenek temankent valtoznak, ezek nem.
  const fixSzin = await p.evaluate(() =>
    ['#C9E8D2','#F5E0AC','#F2C4C4','#4FA97F','#D69A2E','#D46A6A','#14202F']
      .every(h => document.documentElement.innerHTML.includes(h)));
  ok(fixSzin, 'a hőfok-színek beégetve állnak (nem témafüggő token)');
  // A lap pasztellje a Szerencsekerek cikkelyeibol jon — ha a kerek palettaja
  // valtozik, ez a sor bukik, es akkor a lapot is at kell szinezni.
  const kerekbol = await p.evaluate(() => {
    const m = document.documentElement.innerHTML.match(/WHEEL_TONES\s*=\s*\[([^\]]*)\]/);
    return m ? m[1] : '';
  });
  ok(['#C9E8D2','#F5E0AC','#F2C4C4'].every(h => kerekbol.includes(h)),
     'és mindhárom a Szerencsekerék palettájából való', kerekbol.replace(/\s+/g,' ').trim());

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
