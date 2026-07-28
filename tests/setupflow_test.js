// v10.160 — Jatekmenet oldal es a hozza tartozo admin kapcsolo
//
// Ket dolgot vedunk itt. Az egyik a kapcsolo: a regi folyamatnak valtozatlanul
// kell mukodnie, kulonben egy elrontott kapcsolas buli kozben elvagja az
// inditast. A masik a felfedezhetoseg: a het jatek-beallito lap eddig KIZAROLAG
// 500 ms-os hosszu nyomasra nyilt, es semmi nem jelezte, hogy letezik. Pont ez
// volt az eredeti panasz — ha a fogaskerek barmikor visszaesne a kartyakrol,
// annak buknia kell.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

const seed = (flowOn) => `
  try { localStorage.setItem('boh_onboarded','1'); localStorage.setItem('boh_games_view','grid'); } catch(e){}
  window.__fbStore['profiles'] = { p_a:{name:'Anna',color:'#5BA0DB',drinkLimit:8}, p_b:{name:'Béla',color:'#E07A5F'} };
  ['stats','game_stats','statEvents','gameStatEvents','seasons','usage'].forEach(k => window.__fbStore[k] = {});
  window.__fbStore['config'] = { homeConfig: { setupFlowEnabled: ${flowOn ? 'true' : 'false'} } };
`;

// A kepernyoket kozvetlenul mountoljuk — a fooldalrol vegigkattintas tobb
// lepesen at torne el, mint amennyit itt merni akarunk.
const MOUNT = (what, sel) => `
  (() => {
    const root = document.createElement('div'); root.id = '__g';
    root.style.cssText = 'position:fixed;inset:0;z-index:99999;background:#fff;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const PLAYERS = [
      { id:'a', name:'Anna', color:'#5BA0DB', profileId:'p_a' },
      { id:'b', name:'Béla', color:'#E07A5F', profileId:'p_b' },
    ];
    const META0 = { modes:['points'], difficulty:'easy', observerAllowed:true };
    function H() {
      const [sel, setSel] = React.useState(${JSON.stringify(sel)});
      const [meta, setMeta] = React.useState(META0);
      window.__sel = sel; window.__meta = meta;
      return React.createElement(${what === 'games' ? 'GamesScreen' : 'SetupScreen'}, {
        go: (n) => { window.__went = n; },
        players: PLAYERS,
        selectedGames: sel, setSelectedGames: setSel,
        gameMeta: meta, setGameMeta: setMeta,
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  })();
`;

const open = async (b, what, flowOn, sel) => {
  const p = await b.newPage({ viewport: { width: 390, height: 1000 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed(flowOn));
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);
  await p.evaluate(MOUNT(what, sel || ['zene','erem','anagramma','kisebb']));
  await p.waitForTimeout(1600);
  p.__errs = errs;
  return p;
};

const txt = (p) => p.evaluate(() => document.querySelector('#__g').innerText.replace(/\s+/g, ' '));

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ─── 1) REGI FOLYAMAT (kapcsolo ki) — valtozatlanul kell mukodnie ───
  console.log('\n===== REGI FOLYAMAT (setupFlowEnabled: false) =====');
  {
    const p = await open(b, 'games', false);
    const t = await txt(p);
    ok('az indito gomb "Játék indítása"', /Játék indítása/i.test(t), t.match(/(Tovább|Játék indítása)[^|]{0,14}/i));
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__g button')].find(x => /Játék indítása/i.test(x.innerText || ''));
      if (btn) btn.click();
    });
    await p.waitForTimeout(400);
    ok('egyenesen a játékba visz', await p.evaluate(() => window.__went) === 'play', await p.evaluate(() => window.__went));
    // a regi uton a jatekmenet a felirat nelkuli fogaskerek mogott marad
    const gear = await p.evaluate(() => document.querySelectorAll('#__g [data-gameplay-sheet]').length);
    ok('a Játékmenet-lap gombja megvan az alsó sávban', gear === 1, gear + ' db');
    const steps = await p.evaluate(() => {
      const el = document.querySelector('#__g [data-steps]'); return el ? +el.dataset.steps : -1; });
    ok('két lépéspont a fejlécben', steps === 2, steps + ' db');
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 2) UJ FOLYAMAT (kapcsolo be) ───
  console.log('\n===== ÚJ FOLYAMAT (setupFlowEnabled: true) =====');
  {
    const p = await open(b, 'games', true);
    const t = await txt(p);
    ok('az indító gomb "Tovább"-ra vált', /Tovább/i.test(t) && !/Játék indítása/i.test(t),
       (t.match(/(Tovább|Játék indítása)/i) || [])[0]);
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__g button')].find(x => /Tovább/i.test(x.innerText || ''));
      if (btn) btn.click();
    });
    await p.waitForTimeout(400);
    ok('a Játékmenet oldalra visz', await p.evaluate(() => window.__went) === 'setup', await p.evaluate(() => window.__went));
    const gear2 = await p.evaluate(() => document.querySelectorAll('#__g [data-gameplay-sheet]').length);
    ok('az alsó sáv fogaskereke eltűnik (ugyanaz a tartalom kap saját oldalt)', gear2 === 0, gear2 + ' db');
    const steps2 = await p.evaluate(() => {
      const el = document.querySelector('#__g [data-steps]'); return el ? +el.dataset.steps : -1; });
    ok('három lépéspont a fejlécben', steps2 === 3, steps2 + ' db');
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 3) A CERUZA-GOMB A KARTYAKON ───
  // Helyesbites a v10.160-hoz: NEM volt lathatatlan a funkcio, mar volt rajta
  // egy lila ceruza-gomb. Ami tenyleg hianyzott: harom jateknal (kisebb,
  // collect, ovfj) sosem jelent meg, mert a kedvencek-sor kulon ternaryja
  // csak negyet sorolt fel a hetbol. Ezert a szam a lenyeg, nem a puszta letezes.
  console.log('\n===== BEÁLLÍTÁS-GOMB A JÁTÉKKÁRTYÁKON =====');
  {
    // Ures valasztassal indulunk: a Busz/Beer Pong kizarolagossagi szabalya
    // kulonben mindent zarol, zarolt jatekon pedig szandekosan nincs fogaskerek
    // (a megnyitasa kijelolne a jatekot, amit a zar epp tilt).
    const p = await open(b, 'games', false, []);
    const n = await p.evaluate(() => document.querySelectorAll('#__g button[aria-label="Beállítások"]').length);
    ok('mind a 7 beállítható játék kap gombot', n >= 7, n + ' db (7 beállítható játék van)');

    // a gomb NEM csak jelzes: meg is nyitja a lapot
    const opened = await p.evaluate(() => {
      const before = document.body.innerText.length;
      const g = document.querySelector('#__g button[aria-label="Beállítások"]');
      if (!g) return 'nincs gomb';
      g.click();
      return before;
    });
    await p.waitForTimeout(700);
    const after = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
    ok('a gombra kattintva megnyílik a beállító lap',
       typeof opened === 'number' && /Beállítás|beállítás|Kész|Rendben/i.test(after),
       (after.match(/.{0,60}beállítás.{0,40}/i) || ['—'])[0]);
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 4) A JATEKMENET OLDAL TARTALMA ───
  console.log('\n===== A JÁTÉKMENET OLDAL =====');
  {
    const p = await open(b, 'setup', true);
    const t = await txt(p);

    ok('a játékmenet-beállítások itt vannak', /MÓDOK/i.test(t) && /NEHÉZSÉGI SZINT/i.test(t) && /JÁTÉKSORREND/i.test(t));
    const steps3 = await p.evaluate(() => {
      const el = document.querySelector('#__g [data-steps]'); return el ? +el.dataset.steps : -1; });
    ok('a harmadik lépés van kiemelve', steps3 === 3, steps3 + ' db');
    // a kivalasztott negybol kettonek van sajat beallitasa (busz, zene)
    ok('csak a beállítható kiválasztott játékok jelennek meg',
       /Zene/i.test(t) && /Kisebb|kisebb/i.test(t) && !/Anagramma/i.test(t),
       (t.match(/Zene.{0,80}/i) || ['—'])[0]);
    // v10.163: a "Játékok beállításai" fejléc is kikerult — a sorok magukert
    // beszelnek (nev + "Beallitasok megnyitasa" + nyil).
    ok('nincs "A játékok beállításai" fejléc', !/A JÁTÉKOK BEÁLLÍTÁSAI/i.test(t),
       (t.match(/.{0,30}JÁTÉKOK BEÁLLÍTÁSAI.{0,30}/i) || ['—'])[0]);
    // v10.161 ota osszecsukhato, alapbol zarva — opcionalis dolog, ne tolja le
    // a lenyeget a kepernyorol. A jelvenynek zart allapotban is latszania kell,
    // kulonben eszre sem venni, hogy van beallitott limit.
    ok('a kortyolási limit alapból össze van csukva',
       /KORTYOLÁSI LIMIT/i.test(t) && !/Anna/.test(t), (t.match(/KORTYOLÁSI LIMIT.{0,30}/i) || ['—'])[0]);
    ok('zárt állapotban is látszik, hány limit van beállítva',
       /1 beállítva/.test(t), (t.match(/KORTYOLÁSI LIMIT.{0,20}/i) || ['—'])[0]);
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__g button')].find(x => /KORTYOLÁSI LIMIT/i.test(x.innerText || ''));
      if (btn) btn.click();
    });
    await p.waitForTimeout(500);
    const t2 = await txt(p);
    ok('kinyitva szerkeszthető', /Anna/.test(t2), (t2.match(/KORTYOLÁSI LIMIT.{0,40}/i) || ['—'])[0]);
    ok('a profilban tárolt limit betöltődik',
       await p.evaluate(() => {
         const inp = [...document.querySelectorAll('#__g input[type="number"]')];
         return inp.some(x => x.value === '8');
       }), 'Anna limitje 8');

    // v10.162: a beallitasok KULON feher dobozokba kerultek, es minden doboz
    // olyan szeles, mint a felso osszefoglalo. A csoportositas is szamit:
    // nehezseg + sorrend + max korok EGY dobozba.
    ok('a törzsben nincs "Játékmenet" felirat (a fejlécben már ott van)',
       !/^\s*JÁTÉKMENET\b/im.test(t.replace(/ /g, ' ')) || (t.match(/JÁTÉKMENET/g) || []).length === 0,
       (t.match(/JÁTÉKMENET/g) || []).length + ' előfordulás');
    ok('nincs többé hangos műsorvezető', !/műsorvezet/i.test(t), (t.match(/.{0,20}űsorvezet.{0,10}/i) || ['—'])[0]);

    const boxes = await p.evaluate(() => {
      const lab = txt => [...document.querySelectorAll('#__g div')]
        .find(d => d.textContent.trim().toLowerCase() === txt);
      const card = el => { let c = el;
        for (let i = 0; i < 5 && c; i++) { c = c.parentElement;
          if (c && getComputedStyle(c).boxShadow !== 'none') return c; }
        return null; };
      const b = k => { const l = lab(k); const c = l && card(l);
        return c ? { w: Math.round(c.getBoundingClientRect().width), el: c } : null; };
      const modes = b('módok'), diff = b('nehézségi szint'), order = b('játéksorrend'),
            max = b('max körök'), other = b('egyéb');
      const summary = [...document.querySelectorAll('#__g div')]
        .find(d => /játékos/i.test(d.textContent) && /perc/i.test(d.textContent)
                && getComputedStyle(d).boxShadow !== 'none');
      return {
        w: { modes: modes && modes.w, other: other && other.w,
             summary: summary && Math.round(summary.getBoundingClientRect().width) },
        egyBenA3: !!(diff && order && max && diff.el === order.el && order.el === max.el),
        modokKulon: !!(modes && diff && modes.el !== diff.el),
        egyebKulon: !!(other && diff && other.el !== diff.el),
      };
    });
    ok('a Módok külön dobozban van', boxes.modokKulon, JSON.stringify(boxes.w));
    ok('nehézség + sorrend + max körök EGY dobozban', boxes.egyBenA3);
    ok('az Egyéb külön dobozban van', boxes.egyebKulon);
    ok('minden doboz olyan széles, mint a felső összefoglaló',
       boxes.w.modes === boxes.w.summary && boxes.w.other === boxes.w.summary,
       `módok=${boxes.w.modes} egyéb=${boxes.w.other} összefoglaló=${boxes.w.summary}`);
    ok('látszik a becsült idő', /perc/i.test(t), (t.match(/~?\d+ ?PERC/i) || ['—'])[0]);

    // beallito lap nyitasa a listabol
    await p.evaluate(() => {
      const b2 = [...document.querySelectorAll('#__g button')].find(x => /Zene/i.test(x.innerText || ''));
      if (b2) b2.click();
    });
    await p.waitForTimeout(700);
    ok('a sorra kattintva megnyílik a játék beállító lapja',
       await p.evaluate(() => document.body.innerText.length) > t.length, 'lap megnyílt');

    // indit
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__g button')].find(x => /Játék indítása/i.test(x.innerText || ''));
      if (btn) btn.click();
    });
    await p.waitForTimeout(400);
    ok('az indítás a játékba visz', await p.evaluate(() => window.__went) === 'play', await p.evaluate(() => window.__went));
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 5) AZ ADMIN KAPCSOLO TENYLEG IR ───
  // A felhasznalo feltetele az volt, hogy a folyamat adminbol allithato legyen.
  // Ha a kapcsolo nem ir a config/homeConfig-ba, a kepernyok sosem ertesulnek rola.
  console.log('\n===== ADMIN KAPCSOLÓ =====');
  {
    const p = await b.newPage({ viewport: { width: 390, height: 1000 } });
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.addInitScript(stub);
    await p.addInitScript(seed(false));
    await p.goto(BASE, { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(3600);
    await p.evaluate(() => {
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__ad';
      root.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column;background:#EFC77A;overflow:auto';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(window.AdminScreen,
        { go:()=>{}, setTheme:()=>{}, currentTheme:'warm' }));
    });
    await p.waitForTimeout(1400);
    for (const lab of ['Rendszer', 'Beállítások']) {
      await p.evaluate(l => {
        const btn = [...document.querySelectorAll('#__ad button')].find(x => x.innerText.trim() === l);
        if (btn) btn.click();
      }, lab);
      await p.waitForTimeout(800);
    }
    const before = await p.evaluate(() => document.querySelector('#__ad').innerText.replace(/\s+/g, ' '));
    ok('a kapcsoló megjelenik az Admin > Rendszer > Beállítások alatt', /Játékmenet oldal/.test(before));
    ok('kikapcsolva a régi utat mutatja', /Játékosok → Játékok → Játék(?! ?menet)/.test(before),
       (before.match(/Játékosok → Játékok[^A-ZÁ]{0,20}/) || ['—'])[0]);

    // a Toggle egy 52x32-es div, nem <button> — geometria alapjan talalunk ra
    const clicked = await p.evaluate(() => {
      const lbl = [...document.querySelectorAll('#__ad div')].find(d => d.textContent.trim() === 'Játékmenet oldal');
      if (!lbl) return 'nincs címke';
      // A Toggle egy 52x32-es div (nem <button>), es a lapon tobb is van.
      // A cimkehez fuggolegesen legkozelebbi az ove.
      const mid = el => { const r = el.getBoundingClientRect(); return r.top + r.height / 2; };
      const sws = [...document.querySelectorAll('#__ad div')].filter(x => {
        const r = x.getBoundingClientRect();
        return Math.round(r.width) === 52 && Math.round(r.height) === 32; });
      if (!sws.length) return 'nincs kapcsoló';
      const target = mid(lbl);
      sws.sort((a, c) => Math.abs(mid(a) - target) - Math.abs(mid(c) - target));
      sws[0].click(); return 'ok';
    });
    ok('a kapcsoló megtalálható és kattintható', clicked === 'ok', clicked);
    await p.waitForTimeout(900);
    const written = await p.evaluate(() =>
      (window.__fbStore['config'] && window.__fbStore['config'].homeConfig) || null);
    ok('bekapcsolva a config/homeConfig-ba írja', written && written.setupFlowEnabled === true, JSON.stringify(written));
    const after = await p.evaluate(() => document.querySelector('#__ad').innerText.replace(/\s+/g, ' '));
    ok('a felirat az új utat mutatja', /Játékosok → Játékok → Játékmenet → Játék/.test(after),
       (after.match(/Játékosok → Játékok[^A-ZÁ]{0,26}/) || ['—'])[0]);
    ok('nincs JS hiba', errs.length === 0, errs.join(' | '));
    await p.close();
  }

  // ─── 6) A LAPOZAS IRANYA ───
  // A kepernyok sorrendje adja az iranyt: elore jobbrol (slideIn), vissza
  // balrol (slideBack). Ami kimarad a listabol, arra az indexOf -1-et ad, es
  // a kepernyo MINDIG balrol jon — igy csuszott be a Jatekmenet oldal rosszul.
  // Ezert nem eleg a 'setup'-ot felvenni: azt kell vedeni, hogy a routerben
  // szereplo OSSZES kepernyo benne legyen.
  console.log('\n===== LAPOZÁS IRÁNYA =====');
  {
    const src = fs.readFileSync('/home/user/bottle-of-heroes/app.src.html', 'utf8');
    const routed = [...src.matchAll(/\{screen===\s*'([a-z]+)'/g)].map(m => m[1]);
    const om = src.match(/const order = \[([\s\S]*?)\];/);
    const order = om ? [...om[1].matchAll(/'([a-z]+)'/g)].map(m => m[1]) : [];
    const missing = [...new Set(routed)].filter(k => !order.includes(k));
    ok('a router minden képernyője szerepel a sorrendben', missing.length === 0,
       missing.length ? 'hiányzik: ' + missing.join(', ') : `${routed.length} képernyő rendben`);
    ok('a Játékmenet a Játékok után, a Játék előtt van',
       order.indexOf('setup') > order.indexOf('games') && order.indexOf('setup') < order.indexOf('play'),
       order.join(' → '));
    ok('az ismeretlen képernyő ELŐRE számít, nem vissza',
       /i === -1 \? order\.length/.test(src), 'posOf fallback');
  }

  // ─── 6) EGY FORRAS: a beallithato jatekok listaja ne csusszon el ───
  console.log('\n===== EGY FORRÁS =====');
  {
    const src = fs.readFileSync('/home/user/bottle-of-heroes/app.src.html', 'utf8');
    const inline = (src.match(/g\.id==='busz' \?/g) || []).length;
    ok('nincs több inline felsorolás a beállítható játékokról', inline === 0, inline + ' db maradt');
    ok('a lista a GAME_CONFIG_DEFS-ből jön', /const GAME_CONFIG_IDS = Object\.keys\(GAME_CONFIG_DEFS\)/.test(src));
  }

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
