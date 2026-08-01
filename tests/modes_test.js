// v10.275 — a MÓDOK kártya: helyes leírások + sűrűbb wildcard-tartományok
//
// Amit ellenőriz:
//   1. a tartományok 3–6 / 6–9 / 9–12 / 12–15, és PERCEK (a felületen ki is
//      van írva, hogy „percenként")
//   2. a felület alapértelmezett gombja ÉS a timer alapértéke UGYANAZ.
//      Ez a valódi kockázat: az alapérték három helyen szerepel (a kijelölt
//      gomb, a timer lo és hi értéke), és ha szétcsúsznak, a felület mást
//      mutat, mint amit az app csinál — némán.
//   3. a három leírás a VALÓDI viselkedést mondja: nincs benne a régi téves
//      „Vesztes esetén…" és „körönként", viszont benne van a Fun mode és a perc.
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

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);

  console.log('\n===== 1. TARTOMÁNYOK =====');
  const r = await p.evaluate(() => WILDCARD_RANGES.map(x => ({ lo: x.lo, hi: x.hi, label: x.label })));
  ok(r.map(x => x.label).join(' ') === '3–6 6–9 9–12 12–15',
     'a négy tartomány 3–6 / 6–9 / 9–12 / 12–15', r.map(x => x.label).join(' '));
  ok(r.every(x => x.hi > x.lo), 'mindegyik növekvő');
  ok(r.every((x, i) => i === 0 || x.lo === r[i - 1].hi), 'hézag és átfedés nélkül folytatólagosak',
     r.map(x => x.lo + '-' + x.hi).join(' '));

  console.log('\n===== 2. A FELÜLET ÉS A TIMER UGYANAZT AZ ALAPÉRTÉKET HASZNÁLJA =====');
  // A felulet oldala: melyik gomb van kijelolve, ha meg semmit nem allitottak.
  const uiDefault = await p.evaluate(() => {
    const root = document.createElement('div'); root.id = '__m';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto;background:#fff';
    document.body.appendChild(root);
    function H() {
      const [meta, setMeta] = React.useState({ modes: ['points', 'wildcard'], difficulty: 'easy' });
      return React.createElement(GameSettingsContent, { meta, setMeta, group: ['modes'] });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
    return null;
  });
  await p.waitForTimeout(1000);
  const ui = await p.evaluate(() => {
    const root = document.getElementById('__m');
    const btns = [...root.querySelectorAll('button')].filter(x => /^\d+–\d+$/.test((x.innerText || '').trim()));
    const mint = (() => { const s = document.createElement('span'); s.style.color = T.mint; document.body.appendChild(s); const v = getComputedStyle(s).color; s.remove(); return v; })();
    const sel = btns.filter(x => getComputedStyle(x).backgroundColor === mint);
    return { db: btns.length, kijelolt: sel.map(x => x.innerText.trim()),
             perc: /percenk[ée]nt/i.test(root.innerText || '') };
  });
  ok(ui.db === 4, 'négy gomb jelenik meg', ui.db + ' db');
  ok(ui.kijelolt.length === 1, 'pontosan egy van kijelölve', ui.kijelolt.join(',') || 'egy sem');
  ok(ui.kijelolt[0] === '6–9', 'az alapértelmezett a 6–9', ui.kijelolt[0]);
  ok(ui.perc, 'a felület kiírja, hogy PERCENKÉNT (a puszta számokból nem derülne ki)');

  // A timer oldala: Math.random()=0 mellett a beütemezett ms pontosan lo*60000.
  // Igy determinisztikusan latszik, milyen alapertekbol dolgozik a timer.
  const timerMs = await p.evaluate(() => new Promise(resolve => {
    const old = document.getElementById('__m'); if (old) old.remove();
    const origRandom = Math.random, origTimeout = window.setTimeout;
    Math.random = () => 0;
    const seen = [];
    window.setTimeout = function (fn, ms) { seen.push(ms); return origTimeout(fn, ms > 5000 ? 999999 : ms); };
    const root = document.createElement('div'); root.id = '__t';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    function H() {
      const [players, setPlayers] = React.useState([
        { id: 'a', name: 'A', color: '#E07A5F', points: 0, drinks: 0 },
        { id: 'b', name: 'B', color: '#4FC2A0', points: 0, drinks: 0 },
      ]);
      return React.createElement(PlayScreen, {
        go: () => {}, players, setPlayers, selectedGames: ['kopapir'], roomCode: null,
        setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
        // SZANDEKOSAN nincs wildcardMin/Max — az alapertelmezest akarjuk merni
        gameMeta: { modes: ['points', 'wildcard'], difficulty: 'easy' },
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
    origTimeout(() => {
      Math.random = origRandom; window.setTimeout = origTimeout;
      resolve(seen.filter(ms => ms >= 60000));
    }, 1500);
  }));
  ok(timerMs.length > 0, 'a wildcard-időzítő beütemez valamit', JSON.stringify(timerMs));
  ok(timerMs.includes(6 * 60000), 'a timer alapértéke is 6 perc — egyezik a kijelölt gombbal',
     timerMs.map(m => (m / 60000) + ' perc').join(', '));
  ok(!timerMs.includes(8 * 60000), 'a régi 8 perces alapérték már nincs sehol');

  console.log('\n===== 3. A LEÍRÁSOK A VALÓDI VISELKEDÉST MONDJÁK =====');
  const info = await p.evaluate(() => ({
    points: TR.hu.modePointsInfo, group: TR.hu.modeGroupInfo, wildcard: TR.hu.modeWildcardInfo,
  }));
  // Pontgyujtes: a lenyeg, hogy kikapcsolva a KORTY sem keletkezik
  ok(/Fun mode/i.test(info.points), 'Pontgyűjtés: kimondja, hogy kikapcsolva „Fun mode"');
  ok(/korty/i.test(info.points), 'Pontgyűjtés: elárulja, hogy a KORTY-ra is hat',
     info.points.slice(0, 70) + '…');
  // Csoportos ivas: a regi szoveg a VESZTESHEZ kotote — a kod nem
  ok(!/vesztes/i.test(info.group), 'Csoportos ivás: NEM köti a vesztéshez (ez volt a téves állítás)',
     info.group.slice(0, 60) + '…');
  ok(/5–10 perc/.test(info.group), 'Csoportos ivás: kiírja az 5–10 perces időzítőt');
  ok(/nehézség/i.test(info.group), 'Csoportos ivás: elmondja, mitől függ a mennyiség');
  // Wildcard: percek, nem korok
  ok(!/körönként/i.test(info.wildcard), 'Wildcard: NEM ír „körönként"-et (percek vannak)',
     info.wildcard.slice(0, 60) + '…');
  ok(/perc/i.test(info.wildcard), 'Wildcard: percről beszél');
  ok(/Dupla|Fordított|Szerencse/.test(info.wildcard),
     'Wildcard: megemlíti a tényleges hatású lapokat');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
