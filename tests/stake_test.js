// v10.257 — korty-számláló a fejlécben · v10.270-től D1 (tét-korong)
//
// Amit ellenőriz:
//   1. minden játék deklarál `stake`-et (különben néma lyuk lenne a fejlécben)
//   2. a kiírt szám tényleg alap × nehézség × wildcard
//   3. tartomány, ha a játék alap tétje is tartomány
//   4. a GYŰRŰ SZÍNE a DIFFICULTY_INFO-ból jön (v10.270: a színes talp helyett)
//   5. wildcard „dupla” alatt sárga gyűrű és a TELJES szorzó
//   6. a Lóverseny tartományt mutat, és a felső határa a létszámmal nő
//   7. korty-követés nélkül sincs korong
//   8. v10.270: SEMMI nem lóg le a fejléc alá, és a korong nem lóg ki oldalt
//   9. a QR-gomb nem takarja a korty-számot
//  11. v10.270: a körváltó képernyő megmutatja a limitet — de csak ha van
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

// v10.270 — a TET-KORONG kiolvasasa a fejlecbol. A nehezseg mar nem szoveges
// talpon jon, hanem a GYURU STROKE-szinebol. A keresest a fejlecre szukitjuk,
// kulonben a mini result-sav "KORTY" felirata is talalat lenne.
const headerScope = () => {
  const root = document.getElementById('__pl') || document.body;
  const bar = [...root.querySelectorAll('div')].find(d => d.style && d.style.paddingTop === '12px');
  return bar || root;
};
const readCap = p => p.evaluate(() => {
  const root = document.getElementById('__pl') || document.body;
  const bar = [...root.querySelectorAll('div')].find(d => d.style && d.style.paddingTop === '12px');
  const scope = bar || root;
  const unit = [...scope.querySelectorAll('span')].find(s => (s.innerText || '').trim().toLowerCase() === 'korty' &&
    getComputedStyle(s).textTransform === 'uppercase');
  if (!unit) return null;
  const face = unit.parentElement;
  const disc = face.parentElement;
  const num = face.querySelector('span');
  const circle = disc.querySelector('svg circle');
  const r = disc.getBoundingClientRect();
  const qr = disc.querySelector('button[title*="QR"]');
  return {
    num: (num.innerText || '').trim(),
    unit: (unit.innerText || '').trim(),
    ring: circle ? getComputedStyle(circle).stroke : null,
    title: disc.getAttribute('title') || '',
    cursor: getComputedStyle(disc).cursor,
    width: Math.round(r.width),
    height: Math.round(r.height),
    bottom: Math.round(r.bottom),
    right: Math.round(r.right),
    qr: qr ? { top: Math.round(qr.getBoundingClientRect().top), numTop: Math.round(num.getBoundingClientRect().top) } : null,
  };
});

// Egy parti felallitasa a megadott jatekkal es beallitassal.
async function setup(p, gameId, opts) {
  await p.evaluate(({ gid, o }) => {
    const old = document.getElementById('__pl'); if (old) old.remove();
    const root = document.createElement('div');
    root.id = '__pl';
    root.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column;z-index:9;background:#EAF2FB';
    document.body.appendChild(root);
    const players = [
      { id:'a', name:'Sere', color:'#4FC2A0', points:0, drinks:0 },
      { id:'b', name:'Luca', color:'#5BA0DB', points:0, drinks:0 },
    ];
    ReactDOM.createRoot(root).render(React.createElement(PlayScreen, {
      players, setPlayers: () => {}, selectedGames: [gid], go: () => {},
      roomCode: o.room || null,
      gameMeta: { modes: o.noScore ? [] : ['points'], difficulty: o.diff || 'easy', observerAllowed: true,
                  ...(o.maxRounds ? { maxRounds: o.maxRounds } : {}),
                  ...(o.cfg || {}) },
      setGameMeta: () => {}, setLastGameRound: () => {}, setScoreHistory: () => {},
    }));
  }, { gid: gameId, o: opts || {} });
  await p.waitForTimeout(700);
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  console.log('\n===== 1. MINDEN JÁTÉK DEKLARÁL TÉTET =====');
  const decl = await p.evaluate(() => {
    const out = { total: 0, missing: [], nulls: [], bad: [] };
    GAMES.forEach(g => {
      out.total++;
      if (!('stake' in g)) { out.missing.push(g.id); return; }
      if (g.stake === null) { out.nulls.push(g.id); return; }
      const s = g.stake;
      if (!Array.isArray(s) || s.length !== 2 || !(s[0] >= 0) || !(s[1] >= s[0])) out.bad.push(g.id + ':' + JSON.stringify(s));
    });
    return out;
  });
  ok(decl.total >= 44, 'megvan az összes játék', decl.total + ' db');
  ok(decl.missing.length === 0, 'mindegyiknek van `stake` mezője', decl.missing.join(', ') || 'nincs hiányzó');
  ok(decl.bad.length === 0, 'a tartományok értelmesek (0 ≤ min ≤ max)', decl.bad.join(', ') || 'mind rendben');
  // Konkret lista, nem "kevesebb mint N": igy egy uj null TUDATOS dontes lesz,
  // nem eszrevetlenul becsuszo valtozas. Ket csoport van benne:
  //   * sajat gazdasagu jatekok (a korty a jatek belso szabalyabol jon)
  //   * v10.276: hataratlan halmozok — ott inkabb SEMMIT mutatunk, mint
  //     rossz szamot (lasd patch_10_276.py)
  // v10.299: a loverseny KIKERULT innen — a felso hatara kiszamolhato
  // (6 x letszam), tehat nem kell talalgatni.
  // v10.302: a kisebb is KIKERULT — a tet felso hatarat a pakli szabja meg.
  // v10.315: a ritmus is KIKERULT — a vesztes a pontkulonbseget issza, a pont
  // 0-ra van vagva, tehat a plafon a nem-csapda felvillanasok szama.
  const VART_NULL = ['beerpong','blackjack','busz','farkasos',
                     'meduza','ovfj','powerhour','ringfire','utveszto'].sort();
  ok(decl.nulls.slice().sort().join(',') === VART_NULL.join(','),
     'pontosan a várt játékok deklarálnak null tétet', decl.nulls.slice().sort().join(', '));

  console.log('\n===== 1b. KONFIGURÁLHATÓ JÁTÉK: A TÉT A BEÁLLÍTÁSBÓL JÖN (v10.276) =====');
  // A bejelentett hiba: Collect 5×5, Nehez (×3) -> a korong "3–9"-et irt,
  // a jatekos 24 kortyot kapott. A `stake` deklaralt konstans volt; a pot
  // viszont a racsmerettol fuggo MAX_POT-ig no.
  for (const [grid, max] of [[4, 4], [5, 8], [6, 12]]) {
    await setup(p, 'collect', { diff: 'hard', cfg: { collectConfig: { gridSize: grid } } });
    const c = await readCap(p);
    ok(c && c.num === `3–${max * 3}`, `Collect ${grid}×${grid} · nehéz: 3–${max * 3} korty`, c && c.num);
  }
  // a jatek sajat plafonja ES a korong UGYANABBOL a forrasbol dolgozik
  const egyForras = await p.evaluate(() => {
    const g = GAMES.find(x => x.id === 'collect');
    return [4, 5, 6].every(n => g.stakeOf({ collectConfig: { gridSize: n } })[1] === COLLECT_MAX_POT[n]);
  });
  ok(egyForras, 'a korong és a játék ugyanazt a COLLECT_MAX_POT-ot használja');
  // Kartyacsata: a korty a gyozelmi kulonbseg -> legfeljebb a korok szama
  for (const r of [3, 5, 7]) {
    await setup(p, 'cardbattle', { diff: 'easy', cfg: { cardbattleConfig: { rounds: r } } });
    const c = await readCap(p);
    ok(c && c.num === `1–${r}`, `Kártyacsata ${r} kör: 1–${r} korty`, c && c.num);
  }
  // A hataratlan halmozoknal NINCS korong — inkabb semmi, mint rossz szam
  for (const gid of ['meduza', 'utveszto']) {
    await setup(p, gid, { diff: 'hard' });
    ok(await readCap(p) === null, `${gid}: nincs korong (nincs valódi felső határ)`);
  }
  // Ritmus (v10.315): VAN korong. A felso hatart a jatek sajat idozitese adja
  // (900→380 ms lathatosag, 150→60 ms res), csokkentve a csapdak aranyaval.
  // A korong es a `ritmusMaxDrinks` UGYANABBOL a fuggvenybol dolgozik — ha a
  // jatek tempoja valtozik, ennek a blokknak buknia kell.
  for (const [dur, trap] of [[20, 0.2], [30, 0.2], [60, 0]]) {
    await setup(p, 'ritmus', { diff: 'easy', cfg: { ritmusConfig: { duration: dur, trapChance: trap } } });
    const varhato = await p.evaluate(([d2, t2]) =>
      ritmusMaxDrinks({ ritmusConfig: { duration: d2, trapChance: t2 } }), [dur, trap]);
    const c2 = await readCap(p);
    ok(c2 && c2.num === `1–${varhato}`,
       `Ritmus ${dur} mp · csapda ${Math.round(trap * 100)}%: 1–${varhato} korty`, c2 && c2.num);
  }

  console.log('\n===== 2. A KIÍRT SZÁM = ALAP × NEHÉZSÉG =====');
  for (const [diff, mult] of [['easy', 1], ['mid', 2], ['hard', 3], ['extreme', 5]]) {
    await setup(p, 'reakcio', { diff });
    const c = await readCap(p);
    ok(c && c.num === String(1 * mult), `Reakció (alap 1) · ${diff}: ${mult} korty`, c && c.num);
    ok(c && new RegExp('×' + mult + '$').test(c.title), `  a szorzó a koppintás-címkében`, c && c.title);
  }

  console.log('\n===== 3. TARTOMÁNY =====');
  await setup(p, 'imposztor', { diff: 'hard' });
  const imp = await readCap(p);
  ok(imp && imp.num === '6–9', 'Imposztor (alap 2–3) · nehéz: 6–9 korty', imp && imp.num);
  ok(imp && imp.unit.toLowerCase() === 'korty', 'a mértékegység ki van írva', imp && imp.unit);

  console.log('\n===== 4. A GYŰRŰ SZÍNE A DIFFICULTY_INFO-BÓL JÖN =====');
  await setup(p, 'reakcio', { diff: 'hard' });
  const hard = await readCap(p);
  const meta = await p.evaluate(() => DIFFICULTY_INFO.find(d => d.id === 'hard'));
  const rgb = h => {
    const n = parseInt(h.slice(1), 16);
    return `rgb(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255})`;
  };
  ok(hard.ring === rgb(meta.tone), 'a gyűrű színe a szint saját színe', hard.ring + ' (várt ' + rgb(meta.tone) + ')');
  ok(hard.title === `${meta.label} ×3`, 'a szint neve + szorzó a címkében', hard.title);
  ok(hard.cursor === 'pointer', 'a korong koppintható', hard.cursor);

  console.log('\n===== 5. GEOMETRIA — v10.270: SEMMI NEM LÓG LE =====');
  ok(hard.width === 54 && hard.height === 54, 'a korong 54×54 px', hard.width + '×' + hard.height);
  ok(hard.right <= 402, 'nem lóg ki a képernyő jobb szélén', 'jobb szél: ' + hard.right);
  const barBottom = await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const bars = [...root.querySelectorAll('div')].filter(d => d.style && d.style.paddingTop === '12px');
    return bars.length ? Math.round(bars[0].getBoundingClientRect().bottom) : null;
  });
  // A regi kapszula 48 px-et logott a fejlec ala, ezert a fejlecnek helyet
  // kellett foglalnia neki. A korong NEM log le — ez a lenyeg.
  ok(barBottom !== null && hard.bottom <= barBottom, 'a korong a fejlécen BELÜL van',
     'korong alja ' + hard.bottom + ' vs fejléc alja ' + barBottom);
  ok(barBottom !== null && barBottom - hard.bottom <= 12,
     'nincs 48 px-es üres sáv a korong alatt', (barBottom - hard.bottom) + ' px');
  const firstContentTop = await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const sc = [...root.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto');
    const el = sc && sc.firstElementChild;
    return el ? Math.round(el.getBoundingClientRect().top) : null;
  });
  ok(firstContentTop !== null && firstContentTop >= hard.bottom,
     'a játék tartalma a korong ALATT kezdődik', 'tartalom teteje ' + firstContentTop);

  console.log('\n===== 6. LÓVERSENY: TARTOMÁNY, ÉS A LÉTSZÁM EMELI (v10.299) =====');
  // A Loverseny sokaig `stake:null` volt ("nem talalunk ki szamot"), majd egy
  // ideig az EPPEN beallitott tetet mutatta. Egyik sem volt igaz:
  //   * a nyertes 0-t iszik  -> az also hatar 0
  //   * a vesztes a SAJAT tetjen felul a nyertesek kalapjabol is kap, tehat
  //     szelso esetben 6 x letszam korty  -> ez a felso hatar
  // A `setup` KET jatekossal indit, tehat az alap 0-12.
  await setup(p, 'loverseny', { diff: 'easy' });
  const lov = await readCap(p);
  ok(lov !== null, 'Lóverseny: VAN korong (nem esik vissza a KÖR gyűrűre)');
  ok(lov && lov.num === '0–12', 'két játékos · könnyű: 0–12 korty', lov && lov.num);
  await setup(p, 'loverseny', { diff: 'hard' });
  const lovH = await readCap(p);
  ok(lovH && lovH.num === '0–36', 'két játékos · nehéz: 0–36 (a nehézség SZOROZ)', lovH && lovH.num);
  // a felso hatar a letszammal no — ezt a stakeOf masodik parametere adja
  const skalaz = await p.evaluate(() => {
    const g = GAMES.find(x => x.id === 'loverseny');
    return [2, 3, 5, 6].map(n => g.stakeOf({}, n)[1]).join(',');
  });
  ok(skalaz === '12,18,30,36', 'a felső határ 6 × létszám (2/3/5/6 fő)', skalaz);
  // a korong a nyers tetet NEM mutatja: a leptetot megnyomva sem valtozik
  const elotte = (await readCap(p)).num;
  await p.evaluate(() => {
    const btn = [...document.querySelectorAll('button')].find(x => (x.innerText || '').trim() === '+');
    if (btn) btn.click();
  });
  await p.waitForTimeout(500);
  const utana = (await readCap(p)).num;
  ok(elotte === utana, 'a tét léptetése NEM írja át a korongot — az tartomány', elotte + ' → ' + utana);

  console.log('\n===== 6b. KISEBB/NAGYOBB: A PAKLI SZABJA A FELSŐ HATÁRT (v10.302) =====');
  // A tet 1-rol indul es minden jo tipp utan +1 (alap) vagy ×2; bukasnal a
  // jatekos a pillanatnyi tetet issza. +1-es modban tehat a lapok szama a
  // plafon (52 × pakli), ×2-ben a KISEBB_X2_DOUBLINGS gyakorlati plafon.
  await setup(p, 'kisebb', { diff: 'easy' });
  const ki1 = await readCap(p);
  ok(ki1 !== null, 'Kisebb/Nagyobb: VAN korong (nem a KÖR gyűrű)', ki1 && ki1.num);
  ok(ki1 && ki1.num === '1–52', 'egy pakli · könnyű: 1–52 korty', ki1 && ki1.num);
  await setup(p, 'kisebb', { diff: 'easy', cfg: { kisebbConfig: { decks: 2 } } });
  const ki2 = await readCap(p);
  ok(ki2 && ki2.num === '1–104', 'két pakli: 1–104 — a felső határ a lapokkal nő', ki2 && ki2.num);
  await setup(p, 'kisebb', { diff: 'hard', cfg: { kisebbConfig: { decks: 1 } } });
  const ki3 = await readCap(p);
  ok(ki3 && ki3.num === '3–156', 'nehéz szinten a nehézség SZOROZ (1–52 × 3)', ki3 && ki3.num);
  await setup(p, 'kisebb', { diff: 'easy', cfg: { kisebbConfig: { stackMode: 'times2' } } });
  const ki4 = await readCap(p);
  ok(ki4 && ki4.num === '1–256', '×2-es tétmódban a duplázás-plafon (2^8)', ki4 && ki4.num);
  // a ket fo gomb EGY SORBAN van, es egyik felirata sem torik
  const gombok = await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const g = [...root.querySelectorAll('button')].filter(x => /Nagyobb|Kisebb/.test(x.innerText || ''));
    return g.map(x => { const r = x.getBoundingClientRect();
      return { y: Math.round(r.top), h: Math.round(r.height), tul: x.scrollWidth > x.clientWidth + 1 }; });
  });
  ok(gombok.length === 2 && gombok[0].y === gombok[1].y,
     'a Nagyobb és a Kisebb EGY sorban van', gombok.map(g => 'y=' + g.y).join(' '));
  ok(gombok.every(g => g.h === 100), 'és a magasságuk marad 100 px', gombok.map(g => g.h).join('/'));
  ok(gombok.every(g => !g.tul), 'a feliratuk nem lóg ki');

  console.log('\n===== 7. KORTY-KÖVETÉS NÉLKÜL =====');
  await setup(p, 'reakcio', { diff: 'hard', noScore: true });
  ok(await readCap(p) === null, 'ha nincs pontozás, nincs korong sem');

  console.log('\n===== 8. ONLINE PARTI: NINCS QR A JELVÉNYEN =====');
  await setup(p, 'reakcio', { diff: 'hard', room: 'ABCD' });
  const online = await readCap(p);
  ok(online && !online.qr, 'a jelvényre NEM kerül QR-gomb', online && JSON.stringify(online.qr));
  ok(online && online.num === '3', 'a korty-szám ugyanúgy látszik', online && online.num);
  // A csatlakoztatas nem veszhet el: a MENU-ben ott a szobakod + QR + megosztas.
  await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const b = [...root.querySelectorAll('button')].find(x => /MENÜ/i.test(x.innerText || ''));
    if (b) b.click();
  });
  await p.waitForTimeout(700);
  const menu = await p.evaluate(() => {
    const t = document.body.innerText.replace(/\s+/g, ' ');
    const qr = [...document.querySelectorAll('button[title*="QR"]')].length;
    return { code: /ABCD/.test(t), qr };
  });
  ok(menu.code, 'a MENÜ-ben ott a szobakód');
  ok(menu.qr >= 1, 'és a QR-gomb is — a csatlakoztatás nem veszett el', menu.qr + ' db');

  console.log('\n===== 9. WILDCARD „DUPLA" =====');
  // A wildcard idozitve sul el. A konfigbol nem lehet 1 percnel rovidebbre
  // venni (Math.max(1, wildcardMin)), ezert az EGY darab 60 000 ms-os idozitot
  // rovidre zarjuk — mas idozito nem hasznal pont ennyit. A paklit a "dupla"
  // hatasra szukitjuk, hogy determinisztikus legyen.
  await p.evaluate(() => {
    window.__WC = WILDCARDS.slice();
    WILDCARDS.length = 0;
    WILDCARDS.push(window.__WC.find(w => w.effect === 'double'));
    const orig = window.setTimeout;
    window.__origTimeout = orig;
    window.setTimeout = function (fn, ms) {
      return orig(fn, ms === 60000 ? 100 : ms);
    };
  });
  await p.evaluate(({ }) => {
    const old = document.getElementById('__pl'); if (old) old.remove();
    const root = document.createElement('div');
    root.id = '__pl';
    root.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column;z-index:9;background:#EAF2FB';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(PlayScreen, {
      players: [{ id:'a', name:'Sere', color:'#4FC2A0', points:0, drinks:0 },
                { id:'b', name:'Luca', color:'#5BA0DB', points:0, drinks:0 }],
      setPlayers: () => {}, selectedGames: ['reakcio'], go: () => {}, roomCode: null,
      gameMeta: { modes:['points','wildcard'], difficulty:'hard', wildcardMin:1, wildcardMax:1, observerAllowed:true },
      setGameMeta: () => {}, setLastGameRound: () => {}, setScoreHistory: () => {},
    }));
  }, {});
  await p.waitForTimeout(1600);
  const wc = await readCap(p);
  ok(wc && wc.num === '6', 'dupla wildcard alatt a szám a TELJES szorzóval megy (1 × 3 × 2)', wc && wc.num);
  ok(wc && wc.title === 'Nehéz ×6', 'a címke is a teljes szorzót mutatja, nem két külön számot', wc && wc.title);
  const yellow = await p.evaluate(() => {
    const c = document.createElement('span'); c.style.color = T.yellow; document.body.appendChild(c);
    const v = getComputedStyle(c).color; c.remove(); return v;
  });
  ok(wc && wc.ring === yellow, 'és a gyűrű sárgára vált', wc && wc.ring + ' (várt ' + yellow + ')');
  await p.evaluate(() => {
    WILDCARDS.length = 0; window.__WC.forEach(w => WILDCARDS.push(w));
    window.setTimeout = window.__origTimeout;
  });

  console.log('\n===== 10. NEHÉZSÉG-MAGYARÁZÓ KOPPINTÁSRA =====');
  await setup(p, 'imposztor', { diff: 'mid' });
  await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const bar = [...root.querySelectorAll('div')].find(d => d.style && d.style.paddingTop === '12px');
    const unit = [...(bar || root).querySelectorAll('span')].find(s => (s.innerText || '').trim().toLowerCase() === 'korty' &&
      getComputedStyle(s).textTransform === 'uppercase');
    unit.parentElement.parentElement.click();   // face -> korong
  });
  await p.waitForTimeout(600);
  const sheet = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  ok(/Nehézségi szintek/.test(sheet), 'megnyílik a nehézség-magyarázó lap');
  ok(/alap 2–3 korty × közepes \(2\) = 4–6 korty/.test(sheet),
     'és kiírja a KONKRÉT bontást', (sheet.match(/alap[^.]{0,60}/) || [''])[0]);

  console.log('\n===== 11. KÖRVÁLTÓ KÉPERNYŐ: A LIMIT (v10.270) =====');
  // A korszam kikerult a fejlecbol, tehat a haladast a korvalto kepernyo viszi.
  // Az induló popup a 1. kort mutatja — ott olvassuk ki. (1500 ms utan tunik.)
  const readPopup = () => p.evaluate(() => {
    const el = [...document.querySelectorAll('div')].find(d =>
      d.style && d.style.zIndex === '9998');
    if (!el) return { nyitva: false };
    const t = (el.innerText || '').replace(/\s+/g, ' ').trim();
    const track = [...el.querySelectorAll('div')].find(d =>
      d.style && d.style.height === '7px' && d.style.borderRadius === '4px');
    const fill = track && track.firstElementChild;
    return {
      nyitva: true, szoveg: t,
      savSzelesseg: track ? Math.round(track.getBoundingClientRect().width) : null,
      kitoltesPct: (track && fill) ? Math.round(100 * fill.getBoundingClientRect().width / track.getBoundingClientRect().width) : null,
    };
  });

  await setup(p, 'reakcio', { diff: 'easy', maxRounds: 20 });
  const lim = await readPopup();
  ok(lim.nyitva, 'a körváltó képernyő megjelenik induláskor');
  ok(/1\. Kör/i.test(lim.szoveg), 'a nagy szám az aktuális kör', (lim.szoveg || '').slice(0, 40));
  ok(/20-BÓL/i.test(lim.szoveg), '20 körös limitnél kiírja, hogy „20-ból”', (lim.szoveg.match(/20-BÓL.{0,20}/i) || [''])[0]);
  ok(/MÉG 19 KÖR/i.test(lim.szoveg), 'és hogy még 19 kör van hátra');
  ok(lim.savSzelesseg !== null, 'van haladás-csík');
  ok(lim.kitoltesPct === 5, 'a csík 1/20 = 5%-on áll', lim.kitoltesPct + '%');

  await setup(p, 'reakcio', { diff: 'easy' });   // maxRounds nelkul = vegtelen
  const inf = await readPopup();
  ok(inf.nyitva, 'végtelen módban is megjelenik a körváltó képernyő');
  ok(!/-BÓL/i.test(inf.szoveg), 'de NEM ír limitet — nincs mihez mérni', (inf.szoveg || '').slice(0, 40));
  ok(inf.savSzelesseg === null, 'és nincs haladás-csík sem');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
