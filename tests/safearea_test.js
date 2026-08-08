// Safe area + felső státuszsáv — visszatérő hiba elleni védelem
// Magyarázat és hibakeresési útmutató: docs/safe-area.md
//
// FONTOS: böngészőben env(safe-area-inset-*) = 0, tehát ez a hibaosztály
// "ránézésre" NEM reprodukálható. Ezért itt két dolgot hamisítunk:
//   a) env() értékek behelyettesítése az index.html egy másolatába
//   b) navigator.standalone és screen.height felülírása addInitScript-tel
//
// Amit ellenőriz:
//   1. az alsó holt-zóna korrekciója CSAK a konkrét iOS-aláírásra aktiválódik
//      (screen.height - innerHeight == env(safe-area-inset-top)), minden más
//      készülék-konfiguráción kikapcsolva marad
//   2. a korrekció bekapcsolva a teljes képernyős elemeket a fizikai kijelző
//      aljáig húzza, és az eredmény NEM függ a 100dvh értékétől
//   3. a felső státuszsáv színe követi a képernyő tetejét, és akkor is helyes,
//      ha a position:fixed réteg nem fest (iOS így viselkedik)

const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const TMP = path.join(__dirname, '.safearea_tmp');
const stub = fs.readFileSync(path.join(__dirname, 'fbstub.js'), 'utf8');

let fail = 0;
const ok = (cond, name, extra) => {
  console.log((cond ? '  OK  ' : '  HIBA') + '   ' + name + (extra !== undefined ? '  → ' + extra : ''));
  if (!cond) fail++;
};

// index.html másolat, amiben az env()/100dvh konkrét értékekre cserélve
function makeSim(envTop, envBot, dvh) {
  if (!fs.existsSync(TMP)) fs.mkdirSync(TMP);
  let h = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  h = h.split('env(safe-area-inset-top)').join(envTop + 'px')
       .split('env(safe-area-inset-bottom, 0px)').join(envBot + 'px')
       .split('env(safe-area-inset-bottom)').join(envBot + 'px')
       .split('100dvh').join(dvh + 'px');
  const f = path.join(TMP, `sim_${envTop}_${envBot}_${dvh}.html`);
  fs.writeFileSync(f, h);
  return f;
}

async function open(b, { file, standalone, screenH, innerH }) {
  const p = await b.newPage({ viewport: { width: 402, height: innerH }, deviceScaleFactor: 2 });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  let init = `try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}
    Object.defineProperty(window.screen,'height',{get:()=>${screenH},configurable:true});`;
  if (standalone) init += `Object.defineProperty(navigator,'standalone',{get:()=>true,configurable:true});`;
  await p.addInitScript(init);
  await p.goto('file://' + file, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

const gotoPlayers = async (p) => {
  await p.evaluate(() => { const x = [...document.querySelectorAll('button')].find(e => /^Játék$/.test((e.innerText || '').trim())); if (x) x.click(); });
  await p.waitForTimeout(1300);
};

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. Aláírás-ellenőrzés: hol kapcsoljon BE a korrekció? ──
  // A screen.height a FIZIKAI kijelzőt adja — aláírás-ellenőrzés nélkül
  // elrontaná az ablakos/osztott képernyős eseteket. Lásd docs/safe-area.md 2.
  console.log('\n===== 1. A KORREKCIÓ CSAK A KONKRÉT iOS-ALÁÍRÁSRA =====');
  const cases = [
    { tag: 'iPhone PWA, holt-zónával',      standalone: 1, screenH: 874,  innerH: 812, envTop: 62, envBot: 34, dvh: 812, expect: true },
    { tag: 'iPhone PWA, holt-zóna nélkül',  standalone: 1, screenH: 874,  innerH: 874, envTop: 62, envBot: 34, dvh: 874, expect: false },
    { tag: 'régi iPhone (nincs notch)',     standalone: 1, screenH: 667,  innerH: 667, envTop: 0,  envBot: 0,  dvh: 667, expect: false },
    { tag: 'iPad Split View',               standalone: 1, screenH: 1180, innerH: 600, envTop: 24, envBot: 20, dvh: 600, expect: false },
    { tag: 'Android PWA',                   standalone: 1, screenH: 800,  innerH: 800, envTop: 0,  envBot: 24, dvh: 800, expect: false },
    { tag: 'böngésző (nem telepített)',     standalone: 0, screenH: 874,  innerH: 812, envTop: 62, envBot: 34, dvh: 812, expect: false },
  ];
  for (const c of cases) {
    const p = await open(b, { file: makeSim(c.envTop, c.envBot, c.dvh), standalone: c.standalone, screenH: c.screenH, innerH: c.innerH });
    const v = await p.evaluate(() => window.__bohVh);
    const on = !!(v && v.appH);
    ok(on === c.expect, `${c.tag} → korrekció ${c.expect ? 'BE' : 'KI'}`,
       `hiány=${v && v.deficit} envTop=${v && v.envTop} → ${on ? 'BE' : 'KI'}`);
    await p.close();
  }

  // ── 2. Bekapcsolva: a kijelző aljáig, a 100dvh-tól FÜGGETLENÜL ──
  // A 100dvh iOS-en nem következetes (egyszer 812, egyszer 874 volt ugyanabban
  // az appban), ezért a layout nem támaszkodhat rá. Lásd docs/safe-area.md 2.
  console.log('\n===== 2. A LAYOUT NE FÜGGJÖN A 100dvh-TÓL =====');
  const results = [];
  for (const dvh of [812, 874]) {
    const p = await open(b, { file: makeSim(62, 34, dvh), standalone: 1, screenH: 874, innerH: 812 });
    await gotoPlayers(p);
    const m = await p.evaluate(() => {
      const wrap = [...document.querySelectorAll('div')].find(e => getComputedStyle(e).paddingTop === '62px' && e.style.height);
      const btn = [...document.querySelectorAll('button')].find(e => /Tovább a játékokhoz/.test(e.innerText || ''));
      return { wrapBottom: wrap ? Math.round(wrap.getBoundingClientRect().bottom) : null,
               btnBottom: btn ? Math.round(btn.getBoundingClientRect().bottom) : null };
    });
    results.push({ dvh, ...m });
    ok(m.wrapBottom === 874, `100dvh=${dvh}: a konténer a fizikai kijelző aljáig ér`, `${m.wrapBottom} (várt 874)`);
    ok(m.btnBottom === 840, `100dvh=${dvh}: a gomb a home indicator fölött áll`, `${m.btnBottom} (várt 840 = 874-34)`);
    ok(p.__errs.length === 0, `100dvh=${dvh}: nincs JS hiba`, p.__errs.join(' | '));
    await p.close();
  }
  ok(results[0].btnBottom === results[1].btnBottom,
     'a kétféle 100dvh AZONOS elrendezést ad (nincs rá támaszkodás)',
     `${results[0].btnBottom} vs ${results[1].btnBottom}`);

  // ── 3. Felső státuszsáv színe ──
  // iOS a position:fixed rétegeket üresnek látja a státuszsáv mögött, ezért a
  // színnek a FOLYAMBAN LÉVŐ tartalomból kell jönnie. Lásd docs/safe-area.md 1.
  console.log('\n===== 3. A FELSŐ STÁTUSZSÁV SZÍNE =====');
  const stripColor = async (p, killFixed) => {
    if (killFixed) {
      await p.evaluate(() => document.querySelectorAll('div').forEach(e => {
        const cs = getComputedStyle(e);
        if (cs.position === 'fixed' && cs.zIndex === '55') e.remove();
      }));
      await p.waitForTimeout(120);
    }
    const shot = await p.screenshot({ clip: { x: 190, y: 25, width: 4, height: 4 } });
    // PNG helyett egyszerűbb: a lap tetején lévő pixelt a DOM-ból nem tudjuk,
    // ezért a képernyőkép középső pixelét nézzük meg
    return shot;
  };
  for (const killFixed of [false, true]) {
    const label = killFixed ? 'iOS-szimuláció (fix réteg nem fest)' : 'böngésző/Android (fix réteg fest)';
    // főoldal: nincs fejléc → a téma háttere a helyes
    let p = await open(b, { file: makeSim(62, 34, 812), standalone: 1, screenH: 874, innerH: 812 });
    if (killFixed) await p.evaluate(() => document.querySelectorAll('div').forEach(e => {
      const cs = getComputedStyle(e); if (cs.position === 'fixed' && cs.zIndex === '55') e.remove(); }));
    await p.waitForTimeout(150);
    let png = await p.screenshot({ clip: { x: 200, y: 30, width: 2, height: 2 } });
    const home = png.toString('base64');
    await p.close();

    // Játékosok: fehér AppBar → a sávnak is fehérnek kell lennie
    p = await open(b, { file: makeSim(62, 34, 812), standalone: 1, screenH: 874, innerH: 812 });
    await gotoPlayers(p);
    if (killFixed) await p.evaluate(() => document.querySelectorAll('div').forEach(e => {
      const cs = getComputedStyle(e); if (cs.position === 'fixed' && cs.zIndex === '55') e.remove(); }));
    await p.waitForTimeout(150);
    png = await p.screenshot({ clip: { x: 200, y: 30, width: 2, height: 2 } });
    const players = png.toString('base64');
    const themeColor = await p.evaluate(() => document.querySelector('meta[name="theme-color"]').getAttribute('content'));
    await p.close();

    ok(home !== players, `${label}: a sáv színe követi a képernyőt (főoldal ≠ Játékosok)`);
    ok(themeColor.toUpperCase() === '#FFFFFF',
       `${label}: a theme-color is fehér AppBar-os képernyőn`, themeColor);
  }

  // ── 4. Teljes képernyős FIX rétegek: a tartalom a státuszsáv ALATT kezdődjön ──
  // A `position:fixed; top:calc(-1 * envTop); paddingTop:envTop` páros EREDŐJE
  // NULLA: a tartalom pont a fizikai kijelző tetejére kerül, tehát a státuszsáv
  // MÖGÉ. Böngészőben ez nem látszik (env() = 0), készüléken viszont a felső
  // sáv gombjai elérhetetlenek — a Busz „host játszik játékosként" nézetében
  // pont a 🎮 kijárat tűnt el, és a játékos bennragadt.
  console.log('\n===== 4. FIX RÉTEG: A TARTALOM A STÁTUSZSÁV ALATT =====');
  {
    const src = fs.readFileSync(path.join(ROOT, 'app.src.html'), 'utf8');
    // stílus-objektumonként nézzük: van-e pull-up ÉS csak envTop-nyi felső padding
    const bad = (src.match(/style=\{\{[^}]*top:'calc\(-1 \* env\(safe-area-inset-top\)\)'[^}]*\}\}/g) || [])
      .filter(st => /paddingTop:'env\(safe-area-inset-top\)'/.test(st));
    ok(bad.length === 0,
       'nincs olyan fix réteg, ahol a pull-up és a felső padding kioltja egymást',
       bad.length ? bad[0].slice(0, 90) + '…' : '0 db');
  }
  {
    // …és megmutatjuk, mi a HELYES geometria: a helyes wrappperrel a Busz
    // játékos-nézet kijárata (🎮) a szimulált 62 px-es státuszsáv ALATT áll.
    // FIGYELEM: a wrapper itt a TESZTBEN van beégetve (a valódi belépőhöz egy
    // teljes online partit kellene felállítani), tehát ez a blokk a geometriát
    // dokumentálja — a regressziót a fenti FORRÁS-ellenőrzés fogja meg.
    const p = await open(b, { file: makeSim(62, 34, 812), standalone: 1, screenH: 874, innerH: 812 });
    const geo = await p.evaluate(() => {
      const C = (v, s, r) => ({ id: v + s + r, value: v, suit: s, rowIdx: r, faceUp: true });
      const pl = [{ id:'p0', name:'Olcsi', color:'#A78BFA' }, { id:'p1', name:'Sere', color:'#E07A5F' },
                  { id:'p3', name:'Márk', color:'#4C8DD8' }];
      const bs = { phase:'pyramid', settings:{ pyramidRows:5 }, pyramid:[C('8','♥',6)], nextFlipIdx:1,
                   hands:{ p3:[C('10','♦',0), C('3','♣',0), C('K','♥',0)] }, valueCounts:{ '8':1 },
                   initialDrinks:{ p0:0, p1:0, p3:0 } };
      const room = { players: pl.map(x => ({ ...x, drinks:0 })), buszState: bs, buszTakenIds:['p3'] };
      window.__fbStore['rooms'] = { '424242': room };
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const root = document.createElement('div'); root.id = '__p';
      document.body.appendChild(root);
      // UGYANAZ a fix wrapper, mint a PlayScreen „host játszik játékosként" ága
      ReactDOM.createRoot(root).render(
        React.createElement('div', { style: { position:'fixed', top:0, left:0, right:0, bottom:0,
          paddingTop:'62px', boxSizing:'border-box', zIndex:200, display:'flex', flexDirection:'column', background:T.bg } },
          React.createElement(BuszPlayerView, { room, roomCode:'424242', forcedPlayerId:'p3',
            forcedBusIntroShown:true, onBusIntroShown:()=>{}, onSwitchToHost:()=>{} })));
      return null;
    });
    void geo;
    await p.waitForTimeout(1600);
    const m = await p.evaluate(() => {
      const gm = [...document.querySelectorAll('#__p button')].find(x => /🎮/.test(x.innerText || ''));
      return gm ? Math.round(gm.getBoundingClientRect().top) : null;
    });
    ok(m !== null && m >= 62, 'a 🎮 kijárat a státuszsáv ALATT áll', m + ' px (státuszsáv: 62)');
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  await b.close();
  try { fs.rmSync(TMP, { recursive: true, force: true }); } catch (e) {}
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
