// v10.347–352 — DNR gomb a Szűrő mellett, a játékok kedvenc-soros alakban
//
// A 7. blokk a v10.352-é: a mód TÚLÉLI a képernyő-váltást. A `BottleApp`
// feltételes rendereléssel vált, tehát a Játékmenetre lépve a GamesScreen
// LEBOMLIK — enélkül a visszalépés csendben visszakapcsolta a DNR felületet
// arra, aki épp kikapcsolta.
//
// Az alábbi három dolog a v10.347-é, és mindhárom külön elromolhat:
//
//  1. AZ ELRENDEZÉS. Öt felirat 390 px alatt NEM fér ki egy sorba (a legrosszabb
//     eset — számlálós „Szűrő (2)" — 347 px-et kér, egy 375 px-es telefon sora
//     343). ⚠️ A hibás verzió NEM lógott ki a sorból, és nem is vágódott le
//     semmi: a felirat KETTÉTÖRT („Szűrő" / „(1)") a 44 px-es gombon. A `1fr`
//     oszlop `auto` minimuma ugyanis a leghosszabb SZÓ, nem a teljes felirat —
//     tördelhető szöveg alatt a rács boldogan zsugorít. Ezért a fogódzó a
//     szöveg SORAINAK SZÁMA, nem a doboz túlcsordulása: a `scrollWidth` alapú
//     ellenőrzés a hibás verzión is zöld volt (mérve).
//
//  2. A LISTA ALAKJA. A DNR játékok a Kedvencek széles sorai (`FavTile`) —
//     nem rács-csempék. A fogódzó a `.grid-games` HIÁNYA: ha valaki
//     visszaállítaná a csempés listát, a rács azonnal megjelenne.
//
//  3. A KÖLCSÖNÖS KIZÁRÁS a Szűréssel. A Szűrés lapon megmaradt a „DNR
//     Exkluzív" sor (az kategórián belül szűr, és kombinálható a nehézséggel),
//     a gomb viszont reflektor. Egyszerre bekapcsolva fél-állapot lenne.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

// A DNR exkluziv kor — UGYANAZ a szabaly, amit a gameorder_test oriz.
const DNR_NAMES = ['Beer Pong Torna', 'Blackjack', 'Busz', 'Ország-Város', 'Power Hour'];

const open = async (b, W) => {
  const p = await b.newPage({ viewport: { width: W, height: 1400 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');localStorage.setItem('boh_theme','ice');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__g';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:var(--app-bg)';
    document.body.appendChild(root);
    function H() {
      const [sel, setSel] = React.useState([]);
      const [m, sm] = React.useState({ modes:['points'], difficulty:'mid' });
      window.__sel = () => sel;
      return React.createElement(GamesScreen, { go: () => {}, selectedGames: sel,
        setSelectedGames: setSel, gameMeta: m, setGameMeta: sm });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(1500);
  return p;
};

const dnrBtn = p => p.locator('#__g button[data-chip="dnr"]');

// ⚠️ A Szures lap PORTALBA renderel (a `#__g`-n KIVUL), a lista kategoria-fejlecei
// viszont `#__g`-n BELUL vannak — es a fejlec felirata SZO SZERINT „Egyéni".
// Egy sima `querySelectorAll('button')` a fejlecet talalja meg eloszor, tehat a
// kattintas a szekciot csukja be, nem a szurot kapcsolja. Ez nem elmeleti: az
// 5. blokk elso allitasa pont ezen bukott, es a kovetkezo ket allitas UGY ment
// at, hogy soha nem volt aktiv szuro.
const applyFilter = async (p, label) => {
  await p.evaluate(() => {
    const btn = [...document.querySelectorAll('#__g button')].find(x => /^Szűrő/.test(x.textContent.trim()));
    btn && btn.click();
  });
  await p.waitForTimeout(600);
  await p.evaluate((label) => {
    const outside = [...document.querySelectorAll('button')].filter(b => !b.closest('#__g'));
    const row = outside.find(x => x.textContent.trim() === label);
    row && row.click();
    const close = outside.find(x => /Kész|Bezár|Mehet/i.test(x.textContent.trim()));
    close && close.click();
  }, label);
  await p.waitForTimeout(600);
};

const filterLabel = p => p.evaluate(() =>
  [...document.querySelectorAll('#__g button')].find(x => /^Szűrő/.test(x.textContent.trim())).textContent.trim());

// A lista allapota: milyen alakban all, es mi van benne.
const listState = p => p.evaluate(() => {
  const wrap = document.querySelector('#__g');
  const grids = wrap.querySelectorAll('.grid-games').length;
  // FavTile: szeles sor — flex, 18 px sarok, majdnem teljes szelesseg
  const rows = [...wrap.querySelectorAll('div')].filter(d => {
    const cs = getComputedStyle(d);
    const r = d.getBoundingClientRect();
    return cs.display === 'flex' && cs.borderRadius === '18px' && r.width > wrap.clientWidth * 0.7 && r.height > 40;
  });
  const names = rows.map(r => (r.innerText || '').split('\n')[0].trim()).filter(Boolean);
  return { grids, rowCount: rows.length, names,
           sections: (wrap.innerText.match(/^(EGYÉNI|PÁROS|CSAPAT|KEDVENCEK)$/gmi) || []) };
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. A GOMB: ott van, es a fix DNR paros a szine ──
  console.log('\n===== 1. A GOMB =====');
  {
    const p = await open(b, 402);
    ok(await dnrBtn(p).count() === 1, 'pontosan egy DNR gomb van a szűrősoron');
    const chipLook = () => p.evaluate(() => {
      const btn = document.querySelector('#__g button[data-chip="dnr"]');
      const cs = getComputedStyle(btn);
      const filt = [...document.querySelectorAll('#__g button')].find(x => /^Szűrő/.test(x.textContent.trim()));
      return { label: btn.textContent.trim(), bg: cs.backgroundColor, fg: cs.color,
               pressed: btn.getAttribute('aria-pressed'),
               // a Szuro UTAN all, ugyanabban a sorban
               afterFilter: btn.getBoundingClientRect().left >= filt.getBoundingClientRect().right - 1,
               sameRow: Math.abs(btn.getBoundingClientRect().top - filt.getBoundingClientRect().top) < 2 };
    });
    // Alapbol BE van kapcsolva, ezert eloszor a KIkapcsolt allapot szineit
    // meressuk le, majd allitsuk vissza.
    const on = await chipLook();
    await dnrBtn(p).click(); await p.waitForTimeout(400);
    const off = await chipLook();
    await dnrBtn(p).click(); await p.waitForTimeout(400);
    const look = Object.assign({}, on, { bgOn: on.bg, fgOn: on.fg });
    ok(look.label === 'DNR', 'a felirata „DNR"', look.label);
    ok(look.afterFilter && look.sameRow, '402 px-en a Szűrő MELLETT áll, egy sorban', JSON.stringify(look));
    // ⚠️ FIX szinek: ugyanaz a paros, amit a kartyan a ★ DNR EXKLUZIV szalag visz.
    ok(off.bg === 'rgb(14, 14, 24)', 'kikapcsolva sötét háttér (#0E0E18 — mint a szalag)', off.bg);
    ok(off.fg === 'rgb(255, 210, 63)', 'kikapcsolva arany felirat (#FFD23F — mint a szalag)', off.fg);
    // ⚠️ v10.348: a jatekvalaszto a DNR felulettel NYIT, tehat a gomb alapbol
    // BENYOMOTT allapotban all — es arany hattere van, nem sotet.
    ok(look.pressed === 'true', 'alapból BENYOMVA — a DNR felület az alapértelmezés', look.pressed);
    ok(look.bgOn === 'rgb(255, 210, 63)', 'bekapcsolva MEGFORDUL: arany háttér', look.bgOn);
    ok(look.fgOn === 'rgb(14, 14, 24)', 'sötét felirat rajta', look.fgOn);

    // ── 2. ALAPBOL a DNR lista all, KEDVENC-SOROS alakban ──
    console.log('\n===== 2. A DNR LISTA (ALAPERTELMEZES) =====');
    const first = await listState(p);
    ok(first.names.sort().join(' | ') === DNR_NAMES.join(' | '),
       'megnyitáskor pontosan az öt DNR exkluzív játék áll', first.names.join(' | '));
    // ⚠️ EZ a fogodzo az ALAKRA: rács-csempekent visszaallitva azonnal elbukik.
    ok(first.grids === 0, 'NINCS rács — a játékok kedvenc-soros alakban állnak', first.grids);
    ok(first.rowCount === 5, 'öt széles sor', first.rowCount);
    ok(first.sections.length === 0, 'a kategória- és Kedvencek szekciók nem látszanak', first.sections.join(','));
    ok(await p.evaluate(() => /DNR EXKLUZÍV/.test(document.querySelector('#__g').innerText)),
       'ott a „★ DNR EXKLUZÍV" fejléc');

    // KIkapcsolva jon elo a teljes kinalat — enelkul a lista nem lenne elerheto
    await dnrBtn(p).click();
    await p.waitForTimeout(500);
    const full = await listState(p);
    ok(full.grids > 0 && full.sections.length > 0,
       'a gombot KIkapcsolva előjön a teljes lista (rács + szekciók)',
       'rács=' + full.grids + ' szekciók=' + full.sections.join(','));
    ok(await p.evaluate(() => document.querySelector('#__g button[data-chip="dnr"]').getAttribute('aria-pressed')) === 'false',
       'és a gomb kikapcsolt állapotba került');

    // ── 2b. ⚠️ A NORMAL LISTAN NINCS DNR JATEK, es NINCS KEDVENCEK (v10.349) ──
    // Eddig mind az ot DNR jatek ott allt a sajat `Csapat` szekciojaban is,
    // a Kedvencek pedig bedrotozva a `beerpong`-ot es a `busz`-t ismetelte.
    console.log('\n===== 2b. A NORMAL LISTA TARTALMA =====');
    const norm = await p.evaluate((DNR) => {
      const wrap = document.querySelector('#__g');
      const txt = wrap.innerText;
      const tiles = [...wrap.querySelectorAll('.grid-games > div')]
        .map(d => (d.innerText || '').split('\n')[0].trim()).filter(Boolean);
      return { tiles, hasFav: /^KEDVENCEK$/mi.test(txt),
               dnrOnList: DNR.filter(n => tiles.includes(n)) };
    }, DNR_NAMES);
    ok(norm.dnrOnList.length === 0,
       'egyetlen DNR exkluzív játék sincs a kategória-szekciókban',
       norm.dnrOnList.join(', ') || 'egy sem');
    ok(norm.tiles.length > 20, 'a többi játék viszont ott van', norm.tiles.length + ' csempe');
    ok(!norm.hasFav, 'nincs KEDVENCEK szekció');

    // ⚠️ A Szures „DNR Exkluziv" sora is KIKERULT: DNR jatekok nelkul a normal
    // listan ures kepernyot adna. Ha valaki visszatenne, ez elbukik.
    const filterRows = await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__g button')].find(x => /^Szűrő/.test(x.textContent.trim()));
      btn && btn.click();
      return null;
    });
    await p.waitForTimeout(700);
    const sheetTxt = await p.evaluate(() => {
      const out = [...document.querySelectorAll('button')].filter(b => !b.closest('#__g'))
        .map(b => b.textContent.trim());
      const close = out.find(x => /Kész|Bezár|Mehet/i.test(x));
      return { labels: out, has: out.some(x => /DNR Exkluzív/i.test(x)) };
    });
    ok(!sheetTxt.has, 'a Szűrés lapon NINCS „DNR Exkluzív" sor (üres listát adna)',
       sheetTxt.labels.filter(x => /Egyéni|Páros|Csapat|Önálló|DNR/.test(x)).join(' | '));
    await p.evaluate(() => {
      const close = [...document.querySelectorAll('button')].filter(b => !b.closest('#__g'))
        .find(x => /Kész|Bezár|Mehet/i.test(x.textContent.trim()));
      close && close.click();
    });
    await p.waitForTimeout(500);

    // vissza a DNR feluletre a kovetkezo blokkhoz
    await dnrBtn(p).click();
    await p.waitForTimeout(500);

    // ── 3. A soron KIVALASZTHATO a jatek ──
    console.log('\n===== 3. VALASZTAS A SORON =====');
    await p.evaluate(() => {
      const wrap = document.querySelector('#__g');
      const row = [...wrap.querySelectorAll('div')].find(d => {
        const cs = getComputedStyle(d);
        return cs.display === 'flex' && cs.borderRadius === '18px'
            && (d.innerText || '').startsWith('Blackjack');
      });
      row && row.click();
    });
    await p.waitForTimeout(400);
    ok((await p.evaluate(() => window.__sel())).join(',') === 'blackjack',
       'a sorra koppintva kiválasztódik a játék', (await p.evaluate(() => window.__sel())).join(','));

    // ── 4. A KIVALASZTAS TULELI A VALTAST ──
    console.log('\n===== 4. VALTAS KOZBEN A KIVALASZTAS =====');
    await dnrBtn(p).click();
    await p.waitForTimeout(500);
    const back = await listState(p);
    ok(back.grids > 0 && back.sections.length > 0, 'visszajön a normál lista',
       'rács=' + back.grids + ' szekciók=' + back.sections.join(','));
    ok(await p.evaluate(() => window.__sel().join(',')) === 'blackjack',
       'a DNR felületen kiválasztott játék megmarad', await p.evaluate(() => window.__sel().join(',')));
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 5. KOLCSONOS KIZARAS a Szuressel ──
  console.log('\n===== 5. KOLCSONOS KIZARAS =====');
  {
    const p = await open(b, 402);
    // eloszor szuro — ha ez nem fog, a kovetkezo ket allitas URESEN menne at
    await applyFilter(p, 'Egyéni');
    ok(/^Szűrő \(/.test(await filterLabel(p)), 'egy szűrő aktív', await filterLabel(p));

    await dnrBtn(p).click();
    await p.waitForTimeout(500);
    ok(await filterLabel(p) === 'Szűrő', 'a DNR gomb bekapcsolva TÖRLI a szűrőket', await filterLabel(p));
    ok((await listState(p)).grids === 0, 'és tényleg a DNR lista áll');

    // most forditva: szuro bekapcsolasa kikapcsolja a DNR modot
    await applyFilter(p, 'Páros');
    ok(/^Szűrő \(/.test(await filterLabel(p)), 'a szűrő tényleg bekapcsolt', await filterLabel(p));
    ok(await p.evaluate(() => document.querySelector('#__g button[data-chip="dnr"]').getAttribute('aria-pressed')) === 'false',
       'szűrő bekapcsolása KIKAPCSOLJA a DNR módot');
    ok((await listState(p)).grids > 0, 'és a rácsos lista jött vissza');
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 6. ⚠️ AZ ELRENDEZES minden telefonszelessegen ──
  // A hibas verzio nem "logott ki": a felirat CSENDBEN levagodott. Ezert a
  // szoveg-csomopont sajat szelesseget merjuk a gomb belmeretehez kepest.
  console.log('\n===== 6. ELRENDEZES =====');
  for (const W of [360, 375, 390, 402, 430]) {
    const p = await open(b, W);
    // A LEGROSSZABB eset: szamlalos Szuro-felirat (69 px a 47 helyett). Ha ez a
    // lepes nemulna el, a blokk a KESKENY feliratot merne, es atmenne olyan
    // elrendezesen is, ami elesben levagja a szamlalot.
    await applyFilter(p, 'Egyéni');
    ok(/^Szűrő \(/.test(await filterLabel(p)), W + 'px — a számlálós felirat tényleg kint van', await filterLabel(p));

    const m = await p.evaluate(() => {
      const row = document.querySelector('#__g .chipbar');
      const rr = row.getBoundingClientRect();
      const btns = [...row.querySelectorAll(':scope > button')];
      // ⚠️ A TORDELES a fogodzo. A SZOVEG-csomopontra huzott Range
      // `getClientRects()`-je annyi teglalapot ad, ahany sorba a szoveg all —
      // egynel tobb = a felirat kettetort. (A doboz-alapu meres nem fogja meg:
      // tordelesnel nincs tulcsordulas.)
      const wrapped = btns.filter(b => {
        const t = [...b.childNodes].find(n => n.nodeType === 3 && n.nodeValue.trim());
        if (!t) return false;
        const rg = document.createRange(); rg.selectNodeContents(t);
        return rg.getClientRects().length > 1;
      }).map(b => b.textContent.trim());
      // es a szoveg ne is logjon ki a gomb belmeretebol (nowrap mellett ez a
      // masik lehetseges kimenet)
      const clipped = btns.filter(b => {
        const t = [...b.childNodes].find(n => n.nodeType === 3 && n.nodeValue.trim());
        if (!t) return false;
        const rg = document.createRange(); rg.selectNodeContents(b);
        const cs = getComputedStyle(b);
        const inner = b.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
        return rg.getBoundingClientRect().width > inner + 1;
      }).map(b => b.textContent.trim());
      const dnr = document.querySelector('#__g button[data-chip="dnr"]');
      return {
        overflow: Math.round(row.scrollWidth - row.clientWidth),
        wrapped, clipped,
        dnrTop: Math.round(dnr.getBoundingClientRect().top), rowTop: Math.round(rr.top),
        dnrW: Math.round(dnr.getBoundingClientRect().width), rowW: Math.round(rr.width),
        rowH: Math.round(rr.height),
      };
    });
    const inline = m.dnrTop - m.rowTop < 4;
    ok(m.overflow <= 0, W + 'px — a sor nem lóg ki', m.overflow + ' px');
    ok(m.wrapped.length === 0, W + 'px — egyetlen felirat sem törik két sorba', m.wrapped.join(', ') || 'egy sem');
    ok(m.clipped.length === 0, W + 'px — és egyik sem lóg ki a gombjából', m.clipped.join(', ') || 'egy sem');
    if (W >= 390) {
      ok(inline, W + 'px — a DNR a Szűrő mellett, egy sorban');
    } else {
      ok(!inline && m.dnrW >= m.rowW - 2, W + 'px — a DNR a sor ALATT, teljes szélességben',
         m.dnrW + ' / ' + m.rowW + ' px');
    }
    await p.close();
  }

  // ── 7. ⚠️ A MOD TULELI A KEPERNYO-VALTAST (v10.352) ──
  // Bejelentes: „ha Jatekmenetrol visszalepek, mindig a DNR felulet jon be, nem
  // pedig az, ahol kivalasztottam a jatekot."
  // A `BottleApp` felteteles renderelessel valt (`{screen==='games' && …}`),
  // tehat a Jatekmenetre lepve a GamesScreen LEBOMLIK — visszaterve uj peldany
  // keletkezik, es a `dnrMode` az alapertelmezesevel indulna.
  console.log('\n===== 7. VISSZALEPES A JATEKMENETROL =====');
  {
    const p = await b.newPage({ viewport: { width: 402, height: 1400 } });
    p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
    await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.addInitScript(stub);
    await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');localStorage.setItem('boh_theme','ice');}catch(e){}`);
    await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(3400);

    // ⚠️ A harness UGYANUGY valt, ahogy a BottleApp: felteteles rendereles,
    // tehat a kepernyo tenyleg LEBOMLIK. (Egy `display:none` nem reprodukalna.)
    await p.evaluate(() => {
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__g';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:var(--app-bg)';
      document.body.appendChild(root);
      function H() {
        const [screen, setScreen] = React.useState('games');
        const [sel, setSel] = React.useState([]);
        const [m, sm] = React.useState({ modes:['points'], difficulty:'mid' });
        window.__go = setScreen;
        return React.createElement(React.Fragment, null,
          screen === 'games' && React.createElement(GamesScreen, { go: () => {}, selectedGames: sel,
            setSelectedGames: setSel, gameMeta: m, setGameMeta: sm }),
          screen === 'setup' && React.createElement('div', null, 'JÁTÉKMENET'));
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    });
    await p.waitForTimeout(1500);

    const pressed = () => p.evaluate(() => {
      const btn = document.querySelector('#__g button[data-chip="dnr"]');
      return btn ? btn.getAttribute('aria-pressed') : 'NINCS';
    });
    ok(await pressed() === 'true', 'megnyitáskor a DNR felület (v10.348 változatlan)');

    await dnrBtn(p).click();
    await p.waitForTimeout(500);
    ok(await pressed() === 'false', 'kikapcsoljuk — a teljes lista áll');
    ok((await listState(p)).grids > 0, 'és tényleg a rácsos lista');

    // el a Jatekmenetre, majd VISSZA
    await p.evaluate(() => window.__go('setup'));
    await p.waitForTimeout(600);
    ok(await p.evaluate(() => /JÁTÉKMENET/.test(document.querySelector('#__g').innerText)),
       'átléptünk a Játékmenetre (a képernyő lebomlott)');
    await p.evaluate(() => window.__go('games'));
    await p.waitForTimeout(900);
    ok(await pressed() === 'false',
       '⚠️ visszalépve NEM kapcsol vissza a DNR felület', await pressed());
    ok((await listState(p)).grids > 0, 'a rácsos lista jött vissza, ahol a játékot kiválasztotta');

    // a SZURO is kikapcsolja a modot — az emlekezetnek AZT is kovetnie kell
    await dnrBtn(p).click(); await p.waitForTimeout(500);   // vissza DNR-re
    ok(await pressed() === 'true', 'vissza a DNR felületre');
    await applyFilter(p, 'Egyéni');
    ok(await pressed() === 'false', 'a szűrő kikapcsolta a módot');
    await p.evaluate(() => window.__go('setup'));
    await p.waitForTimeout(500);
    await p.evaluate(() => window.__go('games'));
    await p.waitForTimeout(900);
    ok(await pressed() === 'false', 'és ez a visszalépést is túléli', await pressed());

    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 7b. KONTROLL: FRISS indításnál MARAD a DNR alapértelmezés ──
  // ⚠️ Enélkül egy „soha többé ne nyisson DNR-rel" regresszió is átmenne — az
  // emlékezet szándékosan MODUL-szintű, nem localStorage.
  console.log('\n===== 7b. KONTROLL — FRISS INDITAS =====');
  {
    const p = await open(b, 402);
    ok(await p.evaluate(() => document.querySelector('#__g button[data-chip="dnr"]').getAttribute('aria-pressed')) === 'true',
       'új oldalbetöltésnél megint a DNR felület nyílik');
    await p.close();
  }

  // ── 7c. a harness hu marad a BottleApp-hoz ──
  // Ha a BottleApp valaha MINDIG mountolva tartana a GamesScreen-t, a 7. blokk
  // harness-e mast merne, mint a valosag.
  {
    const src = fs.readFileSync(ROOT + '/app.src.html', 'utf8');
    ok(/screen==='games'\s*&&\s*<GamesScreen/.test(src),
       'a BottleApp tényleg feltételesen rendereli a GamesScreen-t (ezért kell az emlékezet)');
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
