// v10.347 — DNR gomb a Szűrő mellett, a játékok kedvenc-soros alakban
//
// Három dolgot őriz, és mindhárom külön elromolhat:
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
    const look = await p.evaluate(() => {
      const btn = document.querySelector('#__g button[data-chip="dnr"]');
      const cs = getComputedStyle(btn);
      const filt = [...document.querySelectorAll('#__g button')].find(x => /^Szűrő/.test(x.textContent.trim()));
      return { label: btn.textContent.trim(), bg: cs.backgroundColor, fg: cs.color,
               pressed: btn.getAttribute('aria-pressed'),
               // a Szuro UTAN all, ugyanabban a sorban
               afterFilter: btn.getBoundingClientRect().left >= filt.getBoundingClientRect().right - 1,
               sameRow: Math.abs(btn.getBoundingClientRect().top - filt.getBoundingClientRect().top) < 2 };
    });
    ok(look.label === 'DNR', 'a felirata „DNR"', look.label);
    ok(look.afterFilter && look.sameRow, '402 px-en a Szűrő MELLETT áll, egy sorban', JSON.stringify(look));
    // ⚠️ FIX szinek: ugyanaz a paros, amit a kartyan a ★ DNR EXKLUZIV szalag visz.
    ok(look.bg === 'rgb(14, 14, 24)', 'sötét háttér (#0E0E18 — mint a szalag)', look.bg);
    ok(look.fg === 'rgb(255, 210, 63)', 'arany felirat (#FFD23F — mint a szalag)', look.fg);
    ok(look.pressed === 'false', 'alapból nincs benyomva', look.pressed);

    // ── 2. MEGNYOMVA: csak a DNR jatekok, KEDVENC-SOROS alakban ──
    console.log('\n===== 2. A DNR LISTA =====');
    const before = await listState(p);
    ok(before.grids > 0 && before.sections.length > 0, 'előtte a normál lista áll (rács + szekciók)',
       'rács=' + before.grids + ' szekciók=' + before.sections.join(','));

    await dnrBtn(p).click();
    await p.waitForTimeout(500);
    const after = await listState(p);
    ok(after.names.sort().join(' | ') === DNR_NAMES.join(' | '),
       'pontosan az öt DNR exkluzív játék látszik', after.names.join(' | '));
    // ⚠️ EZ a fogodzo az ALAKRA: rács-csempekent visszaallitva azonnal elbukik.
    ok(after.grids === 0, 'NINCS rács — a játékok kedvenc-soros alakban állnak', after.grids);
    ok(after.rowCount === 5, 'öt széles sor', after.rowCount);
    ok(after.sections.length === 0, 'a kategória- és Kedvencek szekciók eltűntek', after.sections.join(','));
    ok(await p.evaluate(() => /DNR EXKLUZÍV/.test(document.querySelector('#__g').innerText)),
       'ott a „★ DNR EXKLUZÍV" fejléc');
    ok(await p.evaluate(() => document.querySelector('#__g button[data-chip="dnr"]').getAttribute('aria-pressed')) === 'true',
       'a gomb benyomott állapotba került');

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

    // ── 4. KIKAPCSOLVA visszajon a normal lista ──
    console.log('\n===== 4. KIKAPCSOLAS =====');
    await dnrBtn(p).click();
    await p.waitForTimeout(500);
    const back = await listState(p);
    ok(back.grids > 0 && back.sections.length > 0, 'visszajön a normál lista',
       'rács=' + back.grids + ' szekciók=' + back.sections.join(','));
    ok(await p.evaluate(() => window.__sel().join(',')) === 'blackjack',
       'a kiválasztás megmarad', await p.evaluate(() => window.__sel().join(',')));
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

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
