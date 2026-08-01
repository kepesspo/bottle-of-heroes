// v10.257 — korty-számláló a fejlécben
//
// Amit ellenőriz:
//   1. minden játék deklarál `stake`-et (különben néma lyuk lenne a fejlécben)
//   2. a kiírt szám tényleg alap × nehézség × wildcard
//   3. tartomány, ha a játék alap tétje is tartomány
//   4. a nehézségi talp a DIFFICULTY_INFO-ból jön (név, szorzó, szín)
//   5. wildcard „dupla” alatt sárga talp és a TELJES szorzó
//   6. saját gazdaságú játéknál (stake:null) NINCS kapszula — nem találunk ki számot
//   7. korty-követés nélkül sincs kapszula
//   8. a kapszula tényleg kilóg a fejléc alól, és nem lóg ki a képernyőből
//   9. a QR-gomb nem takarja a korty-számot
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

// A kapszula kiolvasasa a fejlecbol: korty-szam + a talp szovege/szine.
const readCap = p => p.evaluate(() => {
  const root = document.getElementById('__pl') || document.body;
  const foot = [...root.querySelectorAll('span')].find(s => /×\d+$/.test((s.innerText || '').trim()) &&
    getComputedStyle(s).textTransform === 'uppercase' && s.previousElementSibling);
  if (!foot) return null;
  const cap = foot.parentElement;
  const spans = [...cap.querySelectorAll(':scope > span')];
  const num = spans[0], unit = spans[1];
  const r = cap.getBoundingClientRect();
  const ring = cap.querySelector('div');
  const qr = cap.querySelector('button[title*="QR"]');
  return {
    num: (num.innerText || '').trim(),
    unit: (unit.innerText || '').trim(),
    foot: (foot.innerText || '').replace(/\s+/g, ' ').trim(),
    footBg: getComputedStyle(foot).backgroundColor,
    width: Math.round(r.width),
    bottom: Math.round(r.bottom),
    right: Math.round(r.right),
    ringBottom: ring ? Math.round(ring.getBoundingClientRect().bottom) : null,
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
      gameMeta: { modes: o.noScore ? [] : ['points'], difficulty: o.diff || 'easy', observerAllowed: true },
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
      if (!Array.isArray(s) || s.length !== 2 || !(s[0] >= 1) || !(s[1] >= s[0])) out.bad.push(g.id + ':' + JSON.stringify(s));
    });
    return out;
  });
  ok(decl.total >= 44, 'megvan az összes játék', decl.total + ' db');
  ok(decl.missing.length === 0, 'mindegyiknek van `stake` mezője', decl.missing.join(', ') || 'nincs hiányzó');
  ok(decl.bad.length === 0, 'a tartományok értelmesek (1 ≤ min ≤ max)', decl.bad.join(', ') || 'mind rendben');
  ok(decl.nulls.length > 0 && decl.nulls.length <= 10,
     'a saját gazdaságú játékok null-t deklarálnak', decl.nulls.join(', '));

  console.log('\n===== 2. A KIÍRT SZÁM = ALAP × NEHÉZSÉG =====');
  for (const [diff, mult] of [['easy', 1], ['mid', 2], ['hard', 3], ['extreme', 5]]) {
    await setup(p, 'reakcio', { diff });
    const c = await readCap(p);
    ok(c && c.num === String(1 * mult), `Reakció (alap 1) · ${diff}: ${mult} korty`, c && c.num);
    ok(c && new RegExp('×' + mult + '$').test(c.foot), `  a talp a szorzót mutatja`, c && c.foot);
  }

  console.log('\n===== 3. TARTOMÁNY =====');
  await setup(p, 'imposztor', { diff: 'hard' });
  const imp = await readCap(p);
  ok(imp && imp.num === '6–9', 'Imposztor (alap 2–3) · nehéz: 6–9 korty', imp && imp.num);
  ok(imp && imp.unit.toLowerCase() === 'korty', 'a mértékegység ki van írva', imp && imp.unit);

  console.log('\n===== 4. A TALP A DIFFICULTY_INFO-BÓL JÖN =====');
  await setup(p, 'reakcio', { diff: 'hard' });
  const hard = await readCap(p);
  const meta = await p.evaluate(() => DIFFICULTY_INFO.find(d => d.id === 'hard'));
  const rgb = h => {
    const n = parseInt(h.slice(1), 16);
    return `rgb(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255})`;
  };
  ok(hard.foot === `${meta.label.toUpperCase()} ×3`, 'a talp felirata a szint neve + szorzó', hard.foot);
  ok(hard.footBg === rgb(meta.tone), 'a talp színe a szint saját színe', hard.footBg + ' (várt ' + rgb(meta.tone) + ')');

  console.log('\n===== 5. GEOMETRIA =====');
  ok(hard.width === 60, 'a kapszula 60 px széles', hard.width + ' px');
  ok(hard.right <= 402, 'nem lóg ki a képernyő jobb szélén', 'jobb szél: ' + hard.right);
  ok(hard.bottom - hard.ringBottom >= 25, 'a korty-rész tényleg lelóg a gyűrű alá',
     (hard.bottom - hard.ringBottom) + ' px-szel');
  const barBottom = await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const bars = [...root.querySelectorAll('div')].filter(d => d.style && d.style.paddingTop === '12px');
    return bars.length ? Math.round(bars[0].getBoundingClientRect().bottom) : null;
  });
  // A fejlec helyet FOGLAL a lelogo resznek — igy a kapszula sehol nem takar
  // tartalmat (v10.258: az Imposztor jatekleirasat vagta el).
  ok(barBottom !== null && hard.bottom <= barBottom, 'a fejléc helyet foglal neki — nem takar tartalmat',
     'kapszula alja ' + hard.bottom + ' vs fejléc alja ' + barBottom);
  const firstContentTop = await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const sc = [...root.querySelectorAll('div')].find(d => d.style && d.style.overflowY === 'auto');
    const el = sc && sc.firstElementChild;
    return el ? Math.round(el.getBoundingClientRect().top) : null;
  });
  ok(firstContentTop !== null && firstContentTop >= hard.bottom,
     'a játék tartalma a kapszula ALATT kezdődik', 'tartalom teteje ' + firstContentTop);

  console.log('\n===== 6. SAJÁT GAZDASÁGÚ JÁTÉK =====');
  await setup(p, 'loverseny', { diff: 'hard' });
  ok(await readCap(p) === null, 'Lóverseny (stake:null): nincs kapszula — nem találunk ki számot');
  const ringOnly = await p.evaluate(() => {
    const root = document.getElementById('__pl');
    return [...root.querySelectorAll('div')].some(d => /KÖR/.test(d.innerText || ''));
  });
  ok(ringOnly, 'a KÖR gyűrű viszont ugyanúgy ott van');

  console.log('\n===== 7. KORTY-KÖVETÉS NÉLKÜL =====');
  await setup(p, 'reakcio', { diff: 'hard', noScore: true });
  ok(await readCap(p) === null, 'ha nincs pontozás, nincs kapszula sem');

  console.log('\n===== 8. QR-GOMB (online parti) =====');
  await setup(p, 'reakcio', { diff: 'hard', room: 'ABCD' });
  const online = await readCap(p);
  ok(online && online.qr, 'online partinál ott a QR-gomb');
  ok(online.qr && online.qr.top < online.qr.numTop,
     'a QR-gomb a korty-szám FÖLÖTT van (nem takarja)',
     'QR teteje ' + (online.qr && online.qr.top) + ' vs szám teteje ' + (online.qr && online.qr.numTop));
  ok(online.num === '3', 'és a szám ugyanúgy látszik', online.num);

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
  ok(wc && wc.foot === 'NEHÉZ ×6', 'a talp is a teljes szorzót mutatja, nem két külön számot', wc && wc.foot);
  const yellow = await p.evaluate(() => {
    const c = document.createElement('span'); c.style.color = T.yellow; document.body.appendChild(c);
    const v = getComputedStyle(c).color; c.remove(); return v;
  });
  ok(wc && wc.footBg === yellow, 'és a talp sárgára vált', wc && wc.footBg + ' (várt ' + yellow + ')');
  await p.evaluate(() => {
    WILDCARDS.length = 0; window.__WC.forEach(w => WILDCARDS.push(w));
    window.setTimeout = window.__origTimeout;
  });

  console.log('\n===== 10. NEHÉZSÉG-MAGYARÁZÓ KOPPINTÁSRA =====');
  await setup(p, 'imposztor', { diff: 'mid' });
  await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const foot = [...root.querySelectorAll('span')].find(s => /×\d+$/.test((s.innerText || '').trim()) &&
      getComputedStyle(s).textTransform === 'uppercase');
    foot.parentElement.click();
  });
  await p.waitForTimeout(600);
  const sheet = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  ok(/Nehézségi szintek/.test(sheet), 'megnyílik a nehézség-magyarázó lap');
  ok(/alap 2–3 korty × közepes \(2\) = 4–6 korty/.test(sheet),
     'és kiírja a KONKRÉT bontást', (sheet.match(/alap[^.]{0,60}/) || [''])[0]);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
