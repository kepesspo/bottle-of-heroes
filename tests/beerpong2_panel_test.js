// v10.384 — Beer Pong 2.0: NINCS „Ki rontott?" csapat-panel
//
// A BEJELENTETT HIBA: a beer pong 2.0-nál a PlayScreen kitette a „KI RONTOTT?"
// csapat-panelt (avatarok + „Senki nem rontott" gomb). Ez azért volt, mert a
// duplikáláskor (v10.376) a `beerpong2` kimaradt a PlayScreen csapat-panel
// KIZÁRÁSI listájából (a régi `beerpong` benne volt). A beer pong maga könyvel
// a meccs-pontozással — a panel egy második, ellentmondó út lett volna a
// könyveléshez. (CLAUDE.md v10.361: „maga-könyvelő csapatjátéknál a hosszú
// id-lista zárja ki, nem a cta:[]".)
//
// Fogódzó: a beer pong 2.0 tényleg RENDERELŐDIK (meccs-lap), de NINCS
// „Ki rontott" / „Senki nem rontott" panel.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3000);

  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:#DCEDE4';
    document.body.appendChild(root);
    function H() {
      const [ps, setPs] = React.useState([
        { id:'a', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
        { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
        { id:'c', name:'Vivi', color:'#A78BFA', points:0, drinks:0 },
        { id:'d', name:'Robi', color:'#5BA0DB', points:0, drinks:0 }]);
      return React.createElement(PlayScreen, { go: () => {}, players: ps, setPlayers: setPs, selectedGames: ['beerpong2'],
        roomCode: null, setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
        gameMeta: { modes: ['points', 'drinks'], difficulty: 'easy', beerpong2Config: { tournamentType:'se', mode:'egyeni', maxCups:10, matchMinutes:0 } } });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(2600);

  const txt = await p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));
  // 1) a beer pong tényleg renderelődött (meccs-lap: VS + a játékos-nevek)
  ok(/VS/.test(txt) && /Sere/.test(txt), 'a Beer Pong 2.0 meccs-lapja renderelődik (VS + nevek)', /VS/.test(txt));
  // 2) NINCS csapat-panel
  ok(!/Ki rontott/i.test(txt), '⚠️ NINCS „Ki rontott?" panel a beer pongnál', !/Ki rontott/i.test(txt));
  ok(!/Senki nem rontott/i.test(txt), 'és NINCS „Senki nem rontott" gomb', !/Senki nem rontott/i.test(txt));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
