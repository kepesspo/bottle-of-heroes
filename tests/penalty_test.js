// v10.204 — Büntetés = korty-kiosztó, Koccintó kivezetve
// v10.212 — fix magassag + gorgetheto nevek + fix gomb, es toast helyett
//           a szokasos result banner
// v10.272 — a Buntetes ALSO LAP helyett MODAL (ugyanaz, mint a wildcard
//           "Szabalyszego?"), soronkent `− szam +`
//
// Amit ellenoriz:
//   1. a MENÜ-ben nincs tobbe Koccinto
//   2. a Buntetes gomb egy korty-kioszto lapot nyit
//   3. a kiosztott korty tenyleg rakerul a jatekosokra (innen megy a
//      parti vegen a statisztikaba)
//   4. a lap bezarul, es a nagy result banner megmondja, ki mennyit kapott
//
// FIGYELEM: a hatterben futo jatek IS kirajzolhat DrinkDistributort
// (pl. Ko-papir-ollo "1. kör — kortyok"), ezert minden kattintast a
// buntetes-lapon BELUL kell keresni.
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
  const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);

  // PlayScreen kozvetlenul, harom jatekossal
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column';
    document.body.appendChild(root);
    function H() {
      const [players, setPlayers] = React.useState([
        { id: 'a', name: 'Sere', color: '#E07A5F', points: 0, drinks: 0 },
        { id: 'b', name: 'Kecsi', color: '#4FC2A0', points: 0, drinks: 0 },
        { id: 'c', name: 'Vivi', color: '#A78BFA', points: 0, drinks: 0 },
      ]);
      window.__players = players;
      return React.createElement(PlayScreen, {
        go: () => {}, players, setPlayers, selectedGames: ['kopapir'],
        roomCode: null, gameMeta: { modes: ['points'], difficulty: 'mid' }, setGameMeta: () => {},
        setScoreHistory: () => {}, setLastGameRound: () => {},
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(2400);

  console.log('\n===== MENÜ =====');
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /MENÜ/i.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(900);
  const menuTxt = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
  ok(!/Koccint/i.test(menuTxt), 'a Koccintó eltűnt a menüből');
  // v10.216 óta a Vissza/Újra/Kövi mellett egységes ikon+szöveg gomb — a
  // gomb szövege önmagában "Büntetés" (a sheet CÍME a hosszabb "Büntetés — ki igyon?")
  const penaltyBtnText = await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => (x.innerText || '').trim() === 'Büntetés'); return b ? b.innerText.trim() : null; });
  ok(penaltyBtnText === 'Büntetés', 'a Büntetés gomb korty-kiosztót ígér', penaltyBtnText);

  console.log('\n===== KORTY KIOSZTÁSA =====');
  await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => (x.innerText || '').trim() === 'Büntetés'); if (b) b.click(); });
  await p.waitForTimeout(1100);

  const clicked = await p.evaluate(() => {
    const titleEl = [...document.querySelectorAll('*')].find(e => (e.textContent || '').trim() === 'Büntetés — ki igyon?');
    let sheet = titleEl;
    while (sheet && !/Senki sem iszik|korty kiosztva/.test(sheet.textContent || '')) sheet = sheet.parentElement;
    if (!sheet) return 'nincs lap';
    window.__sheet = sheet;
    const plus = (name, n) => {
      const lbl = [...sheet.querySelectorAll('div')].find(d => (d.textContent || '').trim() === name && d.children.length === 0);
      if (!lbl) return 'nincs címke: ' + name;
      let row = lbl.parentElement;
      while (row && row.querySelectorAll('button').length < 2) row = row.parentElement;
      if (!row) return 'nincs sor: ' + name;
      const btn = [...row.querySelectorAll('button')].find(x => (x.textContent || '').trim() === '+');
      if (!btn) return 'nincs + gomb: ' + name;
      for (let i = 0; i < n; i++) btn.click();
      return name + ' OK';
    };
    return [plus('Sere', 2), plus('Kecsi', 1)].join(' | ');
  });
  ok(clicked === 'Sere OK | Kecsi OK', 'a lapon minden játékos sora kiosztható', clicked);
  await p.waitForTimeout(500);

  const label = await p.evaluate(() => {
    const b = [...window.__sheet.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || ''));
    return b ? b.innerText.trim() : 'nincs';
  });
  ok(/^3 korty kiosztva/.test(label), 'a záró gomb az összeget mutatja', label);

  await p.evaluate(() => { const b = [...window.__sheet.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || '')); if (b) b.click(); });
  await p.waitForTimeout(900);

  const state = await p.evaluate(() => window.__players.map(x => x.name + ':' + x.drinks).join(','));
  ok(state === 'Sere:2,Kecsi:1,Vivi:0', 'a korty rákerült a játékosokra', state);
  ok(await p.evaluate(() => !document.body.innerText.includes('Büntetés — ki igyon?')), 'a lap bezárult');
  const banner = await p.evaluate(() => document.body.innerText);
  // v10.263: az uj banner nem "Inni kell!"-t ir, hanem az ivok sorat — es
  // fejenkent mas osszegnel (drinks:0) NEM ir ki szamot, csak a jegyzetet.
  ok(/ISZNAK|ISZIK/i.test(banner), 'a nagy result banner feljön');
  ok(!/0 KORTY/i.test(banner), 'és NEM ír ki „0 korty"-ot');
  ok(/Sere 2/.test(banner) && /Kecsi 1/.test(banner), 'a banner megmondja, ki mennyit kapott', (banner.match(/Sere \d[^\n]*Kecsi \d[^\n]*/) || ['nincs'])[0]);

  const real = errs.filter(e => !/ServiceWorker/.test(e));
  ok(real.length === 0, 'nincs JS hiba', real.join(' | '));

  console.log('\n===== SOK JÁTÉKOS — FIX GOMB, GÖRGETHETŐ NEVEK =====');
  const p2 = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs2 = [];
  p2.on('pageerror', e => errs2.push(e.message));
  await p2.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p2.addInitScript(stub);
  await p2.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p2.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p2.waitForTimeout(3600);
  await p2.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column';
    document.body.appendChild(root);
    function H() {
      const names = ['Sere','Kecsi','Vivi','Luca','Tóth','Márk','Dani','KKK','Balázs','Gyula','Bacsi','BB'];
      const [players] = React.useState(names.map((n, i) => ({ id: 'p' + i, name: n, color: '#E07A5F', points: 0, drinks: 0 })));
      return React.createElement(PlayScreen, {
        go: () => {}, players, setPlayers: () => {}, selectedGames: ['kopapir'],
        roomCode: null, gameMeta: { modes: ['points'], difficulty: 'mid' }, setGameMeta: () => {},
        setScoreHistory: () => {}, setLastGameRound: () => {},
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p2.waitForTimeout(2400);
  await p2.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => /MENÜ/i.test(x.innerText || '')); if (b) b.click(); });
  await p2.waitForTimeout(800);
  await p2.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => (x.innerText || '').trim() === 'Büntetés'); if (b) b.click(); });
  await p2.waitForTimeout(1000);
  const geo = await p2.evaluate(() => {
    const titleEl = [...document.querySelectorAll('*')].find(e => (e.textContent || '').trim() === 'Büntetés — ki igyon?');
    const scrollArea = [...document.querySelectorAll('div')].find(d => getComputedStyle(d).overflowY === 'auto' && d.contains(titleEl.parentElement.nextSibling || d));
    const names = ['Sere','Kecsi','Vivi','Luca','Tóth','Márk','Dani','KKK','Balázs','Gyula','Bacsi','BB'];
    const visible = names.filter(n => {
      const lbl = [...document.querySelectorAll('div')].find(d => (d.textContent || '').trim() === n && d.children.length === 0);
      if (!lbl) return false;
      const r = lbl.getBoundingClientRect();
      return r.top >= 0 && r.bottom <= window.innerHeight;
    });
    const btn = [...document.querySelectorAll('button')].find(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || ''));
    const btnR = btn ? btn.getBoundingClientRect() : null;
    return {
      allNamesVisible: visible.length === names.length,
      visibleCount: visible.length,
      btnVisible: btnR ? (btnR.top >= 0 && btnR.bottom <= window.innerHeight) : false,
    };
  });
  ok(!geo.allNamesVisible, 'nem fér ki mind a 12 játékos egyszerre (a lap nem nő végtelenre)', geo.visibleCount + '/12 látszik');
  ok(geo.btnVisible, 'a záró gomb görgetés nélkül is látszik (fix footer)', JSON.stringify(geo));
  // v10.244: a Buntetes lap PONTOSAN olyan magas, mint a MENÜ lap. Korabban a
  // jatekosok szamaval nott: 3 fonel 347 px, 6-nal 503, 8-nal 607 — a MENÜ
  // kozben mindig 365.
  // v10.249: a kozos ertek NEM beegetett szam tobbe. A v10.244-ben rarakott
  // min(365px,82vh) keszuleken levagta a MENÜ tartalmat (mas betumetrika →
  // magasabb tartalom). Most a MENÜ a sajat tartalmahoz igazodik, megmeri
  // magat, es a Buntetes EHHEZ a mert ertekhez igazodik.
  // FONTOS: kereses TARTALOM szerint — a ket lap egyszerre is a DOM-ban lehet
  // (a bezaras animalt), es a puszta "lekerekitett doboz" mindkettore illik.
  const sheetInfo = (which) => p2.evaluate((w) => {
    const sheets = [...document.querySelectorAll('div')].filter(d => {
      const cs = getComputedStyle(d);
      return cs.borderTopLeftRadius === '28px' && cs.flexDirection === 'column' && d.getBoundingClientRect().height > 100;
    });
    const wanted = sheets.find(el => w === 'menu'
      ? /Vezérlés/.test(el.innerText || '')
      : /ki igyon/.test(el.innerText || ''));
    if (!wanted) return null;
    const body = [...wanted.querySelectorAll('div')].find(d => getComputedStyle(d).overflowY === 'auto');
    return {
      h: Math.round(wanted.getBoundingClientRect().height),
      forced: wanted.style.height || '(nincs)',
      scrollH: body ? body.scrollHeight : null,
      clientH: body ? body.clientHeight : null,
    };
  }, which);
  const sheetH = async (w) => { const i = await sheetInfo(w || 'penalty'); return i && i.h; };
  // v10.272: a Buntetes mar NEM also lap, hanem kozepre igazitott modal, tehat
  // nincs mit a MENÜ magassagahoz igazitani. Amit viszont tovabbra is elvarunk:
  // a kartya ne erjen le a kepernyo aljara, es a zaro gomb 12 jatekosnal is
  // gorgetes nelkul latszodjon (ezt fentebb mar ellenoriztuk).
  const modalInfo = await p2.evaluate(() => {
    const ov = [...document.querySelectorAll('div')].filter(d => d.style && d.style.zIndex === '60')
      .find(d => [...d.querySelectorAll('button')].some(x => /korty kiosztva|Senki sem iszik/.test(x.innerText || '')));
    if (!ov) return null;
    const card = ov.firstElementChild;
    const r = card.getBoundingClientRect();
    return { also: Math.round(window.innerHeight - r.bottom), teteje: Math.round(r.top),
             magassag: Math.round(r.height), forced: card.style.height || '(nincs)' };
  });
  ok(modalInfo !== null, 'a Büntetés modalként nyílik (v10.272)');
  ok(modalInfo && modalInfo.also > 20 && modalInfo.teteje > 20,
     'a modal KÖZÉPEN lebeg — nem ér le az aljára, mint az alsó lap',
     modalInfo && ('alul ' + modalInfo.also + ' px, felül ' + modalInfo.teteje + ' px'));
  ok(modalInfo && modalInfo.forced === '(nincs)',
     'és nincs rákényszerítve magasság — a tartalmához igazodik', modalInfo && modalInfo.forced);
  // zarjuk be a buntetest, es nyissuk meg a MENÜ-t ugyanezzel a 12 jatekossal
  await p2.evaluate(() => {
    const x = [...document.querySelectorAll('button')].find(b3 => /korty kiosztva|Senki sem iszik/.test(b3.innerText || ''));
    if (x) x.click();
  });
  await p2.waitForTimeout(900);
  await p2.evaluate(() => { const x = [...document.querySelectorAll('button')].find(b3 => /MENÜ/i.test(b3.innerText || '')); if (x) x.click(); });
  await p2.waitForTimeout(900);
  const menuInfo = await sheetInfo('menu');

  // A MENÜ tartalma NEM lehet levagva: a sajat magassagahoz igazodik, tehat a
  // belso gorgeto sav nem hosszabb, mint a lathato resz. (Ez volt a v10.244
  // regresszio: a rakenyszeritett 365 px keszuleken levagta a gombsort.)
  ok(menuInfo && menuInfo.scrollH !== null && menuInfo.scrollH <= menuInfo.clientH + 1,
     'a MENÜ tartalma nincs levágva (nem kell görgetni)', JSON.stringify(menuInfo));
  ok(menuInfo && menuInfo.forced === '(nincs)',
     'a MENÜ-re nincs rákényszerítve magasság', menuInfo && menuInfo.forced);

  // v10.246: a "valaki iszik" banner belepoje NEM rangathatja oldalra a
  // kartyat — a profilkepek vele mozogtak, ez volt az "ugralas". A keyframe-et
  // kozvetlenul merjuk: raakasztjuk egy dobozra, es kepkockankent nezzuk az X-et.
  const entry = await p2.evaluate(async () => {
    const d = document.createElement('div');
    d.style.cssText = 'position:fixed;top:100px;left:100px;width:200px;height:120px;background:#c00';
    document.body.appendChild(d);
    d.style.animation = 'resultLoseIn .5s ease-out forwards';
    const xs = new Set(), ws = new Set();
    const t0 = performance.now();
    await new Promise(res => {
      const tick = () => {
        const r = d.getBoundingClientRect();
        xs.add(Math.round(r.x * 100) / 100); ws.add(Math.round(r.width * 100) / 100);
        if (performance.now() - t0 < 700) requestAnimationFrame(tick); else res();
      };
      requestAnimationFrame(tick);
    });
    const name = getComputedStyle(d).animationName;
    d.remove();
    // A KOZEPPONT nem mozdulhat: a scale a doboz kozeppontja korul nagyit,
    // ezert az X szelesodik/szukul, de a kozep helyben marad.
    const centers = [...xs].map((x, i) => x + [...ws][i] / 2);
    return { animName: name, distinctX: xs.size, distinctW: ws.size,
             centerSpread: Math.round((Math.max(...centers) - Math.min(...centers)) * 100) / 100 };
  });
  ok(entry.animName === 'resultLoseIn', 'a belépő animáció a rángatás nélküli változat', entry.animName);
  ok(entry.distinctW > 1, 'attól még van "pop" (a méret változik)', `${entry.distinctW} különböző szélesség`);
  ok(entry.centerSpread <= 0.5, 'a kártya KÖZEPE nem mozdul oldalra (nincs rángatás)',
     `eltérés: ${entry.centerSpread} px`);

  const real2 = errs2.filter(e => !/ServiceWorker/.test(e));
  ok(real2.length === 0, 'nincs JS hiba (sok játékos)', real2.join(' | '));
  await p2.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})();
