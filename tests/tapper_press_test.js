// v10.241 — Tapper: a lenyomott tábla (és a rajta ülő profilkép) ne ugorjon
//
// A táblán van egy `transform: scale(...)` lenyomásra, de a transition
// felsorolásból pont a transform maradt ki — így az árnyék és a háttér szépen
// átúszott, a méret viszont pattant. Ujjal ez a parti alatt folyamatosan
// ismétlődik: ez volt a bejelentett "ugrálnak a profilképek játék közben".
//
// Mérve a javítás előtt: az avatar X-e 45 → 49.68 px, azonnal.
//
// Amit ellenőriz:
//   1. a tábla transition-listájában BENNE van a transform
//   2. lenyomáskor a profilkép legfeljebb pár képpontot mozdul
//   3. elengedés után pontosan visszaáll
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

const avatarBox = p => p.evaluate(() => {
  const i = [...document.querySelectorAll('img')].find(x => /char_/.test(x.src || '') && x.getBoundingClientRect().width > 40);
  if (!i) return null;
  const r = i.getBoundingClientRect();
  return { x: Math.round(r.x * 100) / 100, y: Math.round(r.y * 100) / 100, w: Math.round(r.width * 100) / 100 };
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
  await p.waitForTimeout(3600);

  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const av = (typeof CHAR_AVATARS !== 'undefined' && CHAR_AVATARS) || [];
    function H() {
      const [pl, setPl] = React.useState([
        { id:'a', name:'Sere',  color:'#E07A5F', points:0, drinks:0, img: av[0] && av[0].img },
        { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0, img: av[1] && av[1].img },
        { id:'c', name:'Vivi',  color:'#A78BFA', points:0, drinks:0, img: av[2] && av[2].img },
      ]);
      return React.createElement(PlayScreen, {
        go: () => {}, players: pl, setPlayers: setPl, selectedGames: ['tapper'],
        roomCode: null, gameMeta: { modes:['points'], difficulty:'mid' }, setGameMeta: () => {},
        setScoreHistory: () => {}, setLastGameRound: () => {},
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(2600);

  // 1. a transition tartalmazza a transformot
  const tiles = await p.evaluate(() => [...document.querySelectorAll('div')]
    .filter(d => getComputedStyle(d).minHeight === '118px')
    .map(d => { const cs = getComputedStyle(d); return { prop: cs.transitionProperty, dur: cs.transitionDuration }; }));
  ok(tiles.length === 2, 'megvan a két Tapper-tábla', String(tiles.length));
  ok(tiles.every(t => /(^|,\s*)transform(,|$)/.test(t.prop) || t.prop === 'all'),
     'a tábla átúsztatja a transformot is (különben pattan)', JSON.stringify(tiles[0]));

  // 2. lenyomva a profilkep alig mozdul
  const before = await avatarBox(p);
  ok(!!before, 'megvan a profilkép a táblán', JSON.stringify(before));
  await p.mouse.move(before.x + before.w / 2, before.y + before.w / 2);
  await p.mouse.down();
  await p.waitForTimeout(400); // az atuszas veget varjuk meg
  const held = await avatarBox(p);
  const dx = Math.abs(held.x - before.x), dw = Math.abs(held.w - before.w);
  ok(dx <= 3, 'lenyomva a profilkép legfeljebb 3 px-t mozdul', `dx=${dx.toFixed(2)} (a hiba idején 4.68)`);
  ok(dw <= 2, 'és alig kisebb', `dw=${dw.toFixed(2)} (a hiba idején 1.74)`);

  // 3. elengedes utan pontosan vissza
  await p.mouse.up();
  await p.waitForTimeout(500);
  const after = await avatarBox(p);
  ok(after.x === before.x && after.w === before.w, 'elengedés után pontosan visszaáll',
     `${JSON.stringify(before)} → ${JSON.stringify(after)}`);

  // 4. magatol semmi nem mozog (nincs vegtelen animacio az avataron)
  const anims = await p.evaluate(() => {
    const out = [];
    [...document.querySelectorAll('img')].filter(i => /char_/.test(i.src || '')).forEach(i => {
      let n = i, d = 0;
      while (n && d < 6) { const cs = getComputedStyle(n);
        if (cs.animationName !== 'none' && cs.animationIterationCount === 'infinite') out.push(cs.animationName);
        n = n.parentElement; d++; }
    });
    return out;
  });
  ok(anims.length === 0, 'egyetlen profilképen sincs végtelen animáció', anims.join(',') || 'nincs');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
