// v10.355+ — Az új páros játékok és a NEW jelölő
//
// A jelölő a `GAMES[]` bejegyzésen az `isNew:true` mező (ugyanaz a minta, mint
// a `dnr:true`). Két felület olvassa, és mindkettő külön elromolhat:
//   • a kártyán a „★ NEW" szalag,
//   • a Szűrés „Új játékok" sora.
//
// ⚠️ A szalag UGYANOTT áll, ahol a DNR szalag (a kártya alján), ezért a kettő
// kizárja egymást — a teszt ezt külön méri, mert egy jövőbeli `isNew` egy DNR
// játékon két egymásra csúszó szalagot adna.
//
// A játékoknál a fogódzó mindig a BANNER ÉS A KÖNYVELÉS EGYEZÉSE, nem külön a
// kettő: aki a banneren iszik, annak ténylegesen kortyot kell kapnia.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

// Az ÚJ játékok köre. Ha új kerül be, ITT is át kell vezetni — különben a
// 2. blokk elbukik, és nem csendben marad ki a szűrőből.
const NEW_IDS = ['chicken'];

const PL = [{ id:'a', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
            { id:'b', name:'Luca', color:'#4FC2A0', points:0, drinks:0 }];

const open = async (b, { rnd } = {}) => {
  const p = await b.newPage({ viewport: { width: 402, height: 1200 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');localStorage.setItem('boh_theme','ice');}catch(e){}
    ${rnd !== undefined ? `Math.random = function(){ return ${rnd}; };` : ''}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);
  return p;
};

const mountGame = (p, gameId, difficulty) => p.evaluate(({ pl, gameId, difficulty }) => {
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  const old = document.getElementById('__p'); if (old) old.remove();
  const root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
  document.body.appendChild(root);
  function H() {
    const [ps, setPs] = React.useState(pl); window.__players = ps;
    return React.createElement(PlayScreen, { go:()=>{}, players:ps, setPlayers:setPs,
      selectedGames:[gameId], roomCode:null,
      gameMeta:{ modes:['points'], difficulty }, setGameMeta:()=>{},
      setScoreHistory:()=>{}, setLastGameRound:()=>{} });
  }
  ReactDOM.createRoot(root).render(React.createElement(H));
}, { pl: PL, gameId, difficulty });

const tap = (p, re) => p.evaluate(r => {
  const b = [...document.querySelectorAll('#__p button')].find(x => new RegExp(r).test(x.textContent || ''));
  if (!b) return false; b.click(); return true;
}, re.source);

const txt = p => p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));
const state = p => p.evaluate(() => (window.__players || []).map(x => ({ n:x.name, pt:x.points, dr:x.drinks })));

// A banner két oldala — ugyanaz a fogódzó, amit a `wc_reverse_test` használ.
const bannerSides = p => p.evaluate(() => {
  const names = ['Sere', 'Luca'];
  const out = { win: [], lose: [], drinks: null };
  [...document.querySelectorAll('#__p span')].forEach(s => {
    const t = (s.textContent || '').trim().toLowerCase();
    const kind = /^nyertes(ek)?$/.test(t) ? 'win' : /^isz(ik|nak)$/.test(t) ? 'lose' : null;
    if (!kind) return;
    let el = s;
    for (let i = 0; i < 4 && el.parentElement; i++) {
      el = el.parentElement;
      const found = names.filter(n => (el.textContent || '').includes(n));
      if (found.length) { out[kind] = found; return; }
    }
  });
  // ⚠️ A fejlec-korong is „KORTY"-ot ir („1–7 KORTY"), es a DOM-ban ELOBB jon,
  // mint a banner. Naivan szedve a szamot a fejlec TARTOMANYANAK felso vegét
  // kapnank (merve: 7 a 3 helyett). Ezert kihagyjuk azt, ami elott gondolatjel
  // all — az a tartomany, nem a kiosztott korty.
  const all = [...((document.getElementById('__p').innerText || '')
    .matchAll(/(.)?\s*(\d+)\s*KORTY/gi))].filter(m => !/[–-]/.test(m[1] || ''));
  out.drinks = all.length ? parseInt(all[all.length - 1][2], 10) : null;
  return out;
});

const commit = async (p) => { await tap(p, /Kövi/); await p.waitForTimeout(1400); };

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. A JELOLO A KARTYAN ──
  console.log('\n===== 1. A „NEW" SZALAG =====');
  {
    const p = await open(b);
    await p.evaluate(() => {
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__g';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:var(--app-bg)';
      document.body.appendChild(root);
      function H() {
        const [sel, setSel] = React.useState([]);
        const [m, sm] = React.useState({ modes:['points'], difficulty:'mid' });
        return React.createElement(GamesScreen, { go:()=>{}, selectedGames:sel,
          setSelectedGames:setSel, gameMeta:m, setGameMeta:sm });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    });
    await p.waitForTimeout(1500);
    await p.click('#__g button[data-chip="dnr"]');   // ki a DNR felületről
    await p.waitForTimeout(800);

    const badges = await p.evaluate(() => {
      const out = [];
      document.querySelectorAll('.grid-games > div').forEach(t => {
        const name = (t.innerText || '').split('\n')[0].trim();
        if (/★ NEW/.test(t.innerText || '')) out.push(name);
      });
      return out;
    });
    const expected = await p.evaluate((ids) => ids.map(id => (GAMES.find(g => g.id === id) || {}).name), NEW_IDS);
    ok(badges.sort().join(', ') === expected.sort().join(', '),
       'pontosan az új játékokon van „NEW" szalag', badges.join(', ') || 'egy sem');

    // ⚠️ A NEW es a DNR szalag EGY helyen all — sosem eshetnek egymasra.
    const clash = await p.evaluate(() => GAMES.filter(g => g.isNew && (g.id === 'busz' || g.dnr)).map(g => g.id));
    ok(clash.length === 0, 'nincs olyan játék, ami EGYSZERRE új és DNR', clash.join(', ') || 'egy sem');
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));

    // ── 2. A SZURO „Új játékok" SORA ──
    console.log('\n===== 2. A SZURO SORA =====');
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__g button')].find(x => /^Szűrő/.test(x.textContent.trim()));
      btn && btn.click();
    });
    await p.waitForTimeout(700);
    const hasRow = await p.evaluate(() => [...document.querySelectorAll('button')]
      .filter(x => !x.closest('#__g')).some(x => /Új játékok/.test(x.textContent || '')));
    ok(hasRow, 'ott az „Új játékok" sor a Szűrés lapon');
    await p.evaluate(() => {
      const outside = [...document.querySelectorAll('button')].filter(x => !x.closest('#__g'));
      const row = outside.find(x => /Új játékok/.test(x.textContent || ''));
      row && row.click();
      const close = outside.find(x => /Kész|Bezár|Mehet/i.test(x.textContent.trim()));
      close && close.click();
    });
    await p.waitForTimeout(800);
    const shown = await p.evaluate(() => [...document.querySelectorAll('.grid-games > div')]
      .map(t => (t.innerText || '').split('\n')[0].trim()).filter(Boolean));
    ok(shown.sort().join(', ') === expected.sort().join(', '),
       'a szűrő PONTOSAN az új játékokat hagyja meg', shown.join(', '));
    await p.close();
  }

  // ── 3. CHICKEN: ROBBANAS ──
  // `Math.random = 0` -> a robbanas-pont a legkisebb (3), tehat a 3. nyomas robban.
  console.log('\n===== 3. CHICKEN — ROBBANAS =====');
  {
    const p = await open(b, { rnd: 0 });
    await mountGame(p, 'chicken', 'easy');
    await p.waitForTimeout(2000);
    ok(/A KALAPBAN/.test(await txt(p)), 'a kalap kint van', (await txt(p)).slice(0, 60));
    ok(await tap(p, /Kezdés/), 'elindul');
    await p.waitForTimeout(500);
    for (let i = 0; i < 3; i++) { await tap(p, /NYOMOM/); await p.waitForTimeout(400); }
    await p.waitForTimeout(500);
    const s = await bannerSides(p);
    // A kihivo kezd, tehat a 3. nyomas (0. es 2. lepes) MEGINT a kihivoe.
    ok(s.lose.join() === 'Sere' && s.win.join() === 'Luca',
       'aki a robbanó nyomást tette, az iszik — a másik nyer', JSON.stringify(s));
    ok(s.drinks === 3, 'és az EGÉSZ kalapot issza (3)', s.drinks);
    await commit(p);
    const st = await state(p);
    ok(JSON.stringify(st) === JSON.stringify([{n:'Sere',pt:0,dr:3},{n:'Luca',pt:1,dr:0}]),
       '⚠️ a könyvelés EGYEZIK a bannerrel', JSON.stringify(st));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 4. CHICKEN: PASSZ ──
  console.log('\n===== 4. CHICKEN — PASSZ =====');
  {
    const p = await open(b, { rnd: 0 });
    await mountGame(p, 'chicken', 'easy');
    await p.waitForTimeout(2000);
    await tap(p, /Kezdés/);
    await p.waitForTimeout(500);
    ok(!(await p.evaluate(() => [...document.querySelectorAll('#__p button')].some(x => /Passzolok/.test(x.textContent || '')))),
       'ÜRES kalapnál nincs passz — az ingyen pont lenne a másiknak');
    await tap(p, /NYOMOM/); await p.waitForTimeout(400);   // kalap = 1, Luca jön
    ok(await tap(p, /Passzolok/), 'egy nyomás után már lehet passzolni');
    await p.waitForTimeout(700);
    const s = await bannerSides(p);
    ok(s.lose.join() === 'Luca' && s.win.join() === 'Sere',
       'aki passzol, az iszik — a pont a másiké', JSON.stringify(s));
    ok(s.drinks === 1, 'a kalap FELÉT issza (1-ből 1)', s.drinks);
    await commit(p);
    const st = await state(p);
    ok(JSON.stringify(st) === JSON.stringify([{n:'Sere',pt:1,dr:0},{n:'Luca',pt:0,dr:1}]),
       'a könyvelés EGYEZIK a bannerrel', JSON.stringify(st));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 5. A NEHEZSEG SZOROZ, es a banner ugyanazt mondja ──
  // ⚠️ A jatek NYERS szamot kuld mindket csatornan; a szorzas a PlayScreen-ben
  // tortenik. Ha a jatek is szorozna, duplan menne fel.
  console.log('\n===== 5. A NEHEZSEG SZORZOJA =====');
  {
    const p = await open(b, { rnd: 0 });
    await mountGame(p, 'chicken', 'hard');   // ×3
    await p.waitForTimeout(2000);
    await tap(p, /Kezdés/); await p.waitForTimeout(500);
    for (let i = 0; i < 3; i++) { await tap(p, /NYOMOM/); await p.waitForTimeout(400); }
    await p.waitForTimeout(500);
    const s = await bannerSides(p);
    ok(s.drinks === 9, 'nehéz szinten a 3-as kalap 9 kortyot ér a banneren', s.drinks);
    await commit(p);
    const st = await state(p);
    ok(st[0].dr === 9, 'és pontosan ennyi kerül fel — nem 3, és nem 27', JSON.stringify(st));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 6. NINCS kezi eredmeny-gomb (a jatek maga konyvel) ──
  console.log('\n===== 6. NINCS KEZI GOMB =====');
  {
    const p = await open(b, { rnd: 0 });
    await mountGame(p, 'chicken', 'easy');
    await p.waitForTimeout(2000);
    const manual = await p.evaluate(() => [...document.querySelectorAll('#__p button')]
      .map(x => (x.textContent || '').trim()).filter(t => /^(Vesztettem|Nyertem!)/.test(t)));
    ok(manual.length === 0, 'nincs „Vesztettem / Nyertem!" gomb', manual.join(' | ') || 'egy sem');
    ok(await p.evaluate(() => (SCENARIOS.chicken.cta || []).length) === 0,
       'mert a `cta` üres — a játék maga könyvel');
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
