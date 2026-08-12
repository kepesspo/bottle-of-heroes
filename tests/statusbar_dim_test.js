// v10.343 — Modal / bottom sheet alatt a STÁTUSZSÁV is besötétedik
//
// A bejelentés: a „Beállítások" bottom sheet és az „Admin belépés" modal alatt
// az egész lap besötétedik, a felső státuszsáv viszont világos marad, és a
// kettő élesen elválik.
//
// ⚠️ AZ OK a dokumentált iOS-csapda (docs/safe-area.md 1.): black-translucent
// PWA-ban a `position:fixed` rétegek NEM festenek a státuszsáv mögé. A modalok
// sötétítő háttere pontosan ilyen réteg. A sáv színe csak FOLYAMBAN LÉVŐ
// tartalomból (a gyökér konténer háttere) és a `theme-color`-ból jöhet — tehát
// magát a `statusBarBg`-t kell sötétíteni.
//
// ⚠️ EZ BÖNGÉSZŐBEN NEM REPRODUKÁLHATÓ látványként (`env()` = 0), ezért a teszt
// nem képpontot néz, hanem a HÁROM festő csatornát, amit a doksi felsorol:
// a gyökér konténer háttere, a fix festősáv és a `theme-color` meta.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

// A harom festo csatorna EGY forrasbol (statusBarBg) kell jojjon.
const channels = p => p.evaluate(() => {
  // ⚠️ A gyoker KEPERNYO-kontener az, aminek az inline stilusaban ott a
  // `--app-h` — a `#root > div` egy kulso burok, aminek a hattere sosem valtozik,
  // tehat azzal a meres vakon atmenne.
  const root = [...document.querySelectorAll('#root div')]
    .find(d => (d.getAttribute('style') || '').includes('--app-h'));
  const bar = [...document.querySelectorAll('div')].find(d => {
    const cs = getComputedStyle(d);
    return cs.position === 'fixed' && cs.zIndex === '55' && cs.pointerEvents === 'none';
  });
  const meta = document.querySelector('meta[name="theme-color"]');
  const norm = c => (c || '').replace(/\s/g, '');
  return {
    root: root ? norm(getComputedStyle(root).backgroundColor) : null,
    bar: bar ? norm(getComputedStyle(bar).backgroundColor) : null,
    meta: meta ? meta.getAttribute('content') : null,
  };
});
const hexToRgb = h => { const s = h.replace('#',''); return [0,2,4].map(i => parseInt(s.slice(i,i+2),16)); };
const lum = rgb => rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114;
// ⚠️ A ket csatorna MAS alakban adja a szint: a computed style `rgb(...)`-et,
// a theme-color meta viszont hexet. Egy naiv szamjegy-kiszedes a hexbol
// hasznalhatatlant ad (`#E8F4FF` -> 8, 4, 255).
const rgbOf = s => String(s).trim().startsWith('#') ? hexToRgb(String(s).trim())
                 : (String(s).match(/\d+/g) || []).slice(0,3).map(Number);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');localStorage.setItem('boh_theme','ice');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);

  // ── 1. ALAPALLAPOT: nincs fedo reteg ──
  console.log('\n===== 1. ALAPALLAPOT =====');
  const base = await channels(p);
  ok(base.root && base.bar && base.meta, 'mindhárom festő csatorna megvan', JSON.stringify(base));
  ok(base.root === base.bar, 'a gyökér háttere és a festősáv EGYEZIK (egy forrás)', base.root + ' / ' + base.bar);
  ok(rgbOf(base.meta || '#000').join(',') === rgbOf(base.root).join(','),
     'és a theme-color is ugyanaz', base.meta + ' / ' + base.root);

  // ── 2. BOTTOM SHEET: a sav is besotetedik ──
  console.log('\n===== 2. BOTTOM SHEET (Beállítások) =====');
  // A fogaskerek gomb hosszu-nyomas kezelokkel is el van latva (TESZT DB
  // valtas), ezert a puszta `click()` nem megbizhato — a SheetOverlay-t
  // kozvetlenul mountoljuk ugyanazzal a hatterrel, amit a Beallitasok hasznal.
  const opened = await p.evaluate(() => {
    const host = document.createElement('div'); host.id = '__sheet';
    document.body.appendChild(host);
    // ⚠️ A `SheetOverlay` PORTALBA renderel (`document.body`), ezert a host
    // torlese NEM szedne le — a React gyokeret kell lebontani.
    window.__sheetRoot = ReactDOM.createRoot(host);
    window.__sheetRoot.render(
      React.createElement(SheetOverlay, { onClose: () => {}, title: 'Beállítások' },
        React.createElement('div', null, 'TÉMÁK')));
    return 'mountolva';
  });
  await p.waitForTimeout(900);
  let sheetUp = await p.evaluate(() => /Beállítások|TÉMÁK/i.test(document.body.innerText));
  ok(sheetUp, 'a Beállítások lap nyitva van', opened);
  const dim = await channels(p);
  ok(lum(rgbOf(dim.root)) < lum(rgbOf(base.root)) - 8,
     'a gyökér konténer háttere BESÖTÉTEDETT — ez fest a státuszsáv mögé',
     base.root + ' → ' + dim.root);
  ok(dim.root === dim.bar, 'a festősáv is követi (egy forrás)', dim.root + ' / ' + dim.bar);
  ok(rgbOf(dim.meta).join(',') === rgbOf(dim.root).join(','),
     'és a theme-color is — ez fest az első indításnál', dim.meta);

  // ── 3. ZARAS UTAN VISSZAALL ──
  console.log('\n===== 3. ZARAS UTAN =====');
  await p.evaluate(() => {
    if (window.__sheetRoot) window.__sheetRoot.unmount();
    const h = document.getElementById('__sheet'); if (h) h.remove();
  });
  await p.waitForTimeout(900);
  const back = await channels(p);
  ok(back.root === base.root, 'a sáv visszaáll az eredetire', base.root + ' → ' + back.root);

  // ── 4. ⚠️ A DETEKTOR HATARAI ──
  // Nem minden `position:fixed` elem fedo reteg. A festosav maga is fix, es
  // TOMOR — ha az is beszamitana, a sav onmagat sotetitene korrol korre.
  console.log('\n===== 4. A DETEKTOR HATARAI =====');
  const edge = await p.evaluate(() => {
    const mk = (css) => { const d = document.createElement('div'); d.setAttribute('style', css); document.body.appendChild(d); return d; };
    const out = {};
    // teljesen fedo (alpha 1) -> NEM sotetites, hanem egy lap
    const solid = mk('position:fixed;inset:0;background:rgb(10,10,10);z-index:9');
    out.solid = !!bohScanOverlayTint(); solid.remove();
    // alig lathato -> nem szamit
    const faint = mk('position:fixed;inset:0;background:rgba(0,0,0,0.05);z-index:9');
    out.faint = !!bohScanOverlayTint(); faint.remove();
    // kicsi fix elem (pl. lebego gomb) -> nem fedo reteg
    const small = mk('position:fixed;left:0;top:0;width:60px;height:60px;background:rgba(0,0,0,0.6);z-index:9');
    out.small = !!bohScanOverlayTint(); small.remove();
    // valodi fedo reteg -> szamit
    const real = mk('position:fixed;inset:0;background:rgba(14,14,24,0.55);z-index:9');
    out.real = !!bohScanOverlayTint(); real.remove();
    return out;
  });
  ok(edge.solid === false, 'a TELJESEN fedő réteg nem számít sötétítésnek', edge.solid);
  ok(edge.faint === false, 'az alig látható sem', edge.faint);
  ok(edge.small === false, 'a kicsi, lebegő fix elem sem', edge.small);
  ok(edge.real === true, 'a valódi fedő réteg viszont igen', edge.real);

  // ── 5. a szinkevero ──
  console.log('\n===== 5. A SZINKEVERO =====');
  const blend = await p.evaluate(() => ({
    none: bohBlendOver('#FFFFFF', null),
    half: bohBlendOver('#FFFFFF', { r:0, g:0, b:0, a:0.5 }),
    full: bohBlendOver('#FFFFFF', { r:0, g:0, b:0, a:1 }),
    short: bohBlendOver('#FFF', { r:0, g:0, b:0, a:0.5 }),
  }));
  ok(blend.none === '#FFFFFF', 'réteg nélkül változatlan', blend.none);
  ok(blend.half === '#808080', 'félig fedő feketével pont a fele', blend.half);
  ok(blend.full === '#000000', 'teljesen fedővel a réteg színe', blend.full);
  ok(blend.short === '#808080', 'a rövid (#FFF) alakot is érti', blend.short);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
