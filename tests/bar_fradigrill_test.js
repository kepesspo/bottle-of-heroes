// v10.321 — a „Fradi - Grill" shot-sorozat a DNR Pubban
//
// Het beepitett keveres, EGY cimke alatt. Amit ellenoriz:
//   1. mind a het megjelenik a „Mi kevertük" listaban
//   2. a cimke pontosan egyszer szerepel a szuroben, es KISBETUS (a tag-szuro
//      es az `allTags` is toLowerCase()-el dolgozik — egy nagybetus valtozat
//      kulon cimkeve esne szet, es a szuro egyiket sem talalna meg)
//   3. a cimkere kattintva PONTOSAN ez a het marad a listaban
//   4. az aranyok 1 literre vannak szamolva: 295+295+295+115 = 1000 ml
//   5. minden recept mas HELL/Sio parost visz (kulonben ket egyforma ital lenne)
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

const NAMES = ['Tropical Fusion', 'Summer Wave', 'Green Rush', 'Purple Orchard',
               'Berry Wave', 'Berry Garden', 'Melon Breeze'];
const TAG = 'fradi - grill';

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);

  // ── 4-5. az adat maga (a konstans a modul-scope-ban ul, a lapon kiertekelheto) ──
  console.log('\n===== AZ ADAT =====');
  const data = await p.evaluate(() => (typeof FRADI_GRILL_SHOTS === 'undefined' ? null
    : FRADI_GRILL_SHOTS.map(s => ({ id:s.id, name:s.name, emoji:s.emoji, note:s.note,
        tags:s.tags, by:s.by, type:s.type, ing:s.ing }))));
  ok(!!data, 'FRADI_GRILL_SHOTS elerheto a modul-scope-bol');
  ok(data && data.length === 7, 'het recept', data && data.length);
  ok(data && data.every(s => s.type === 'shot'), 'mind shot');
  ok(data && data.every(s => Array.isArray(s.tags) && s.tags.length === 1 && s.tags[0] === TAG),
     'mindegyiken pontosan a „' + TAG + '" cimke (kisbetus)',
     data && JSON.stringify([...new Set(data.flatMap(s => s.tags || []))]));

  const ml = s => s.ing.reduce((a, i) => a + parseInt(i.q, 10), 0);
  ok(data && data.every(s => ml(s) === 1000), '1 literre szamolva (295+295+295+115)',
     data && [...new Set(data.map(ml))].join(','));
  ok(data && data.every(s => s.ing.length === 4 && /Finlandia/.test(s.ing[0].n)
       && /HELL/.test(s.ing[1].n) && /Sió/.test(s.ing[2].n) && /szóda/.test(s.ing[3].n)),
     'mind a negy hozzavalo a helyen (Finlandia / HELL / Sió / szóda)');
  const pairs = data ? data.map(s => s.ing[1].n + ' | ' + s.ing[2].n) : [];
  ok(new Set(pairs).size === 7, 'minden recept MAS HELL+Sió parost visz', new Set(pairs).size);
  ok(data && new Set(data.map(s => s.id)).size === 7 && new Set(data.map(s => s.name)).size === 7,
     'nincs ismetlodo id / nev');
  ok(data && data.every(s => s.note && s.note.length > 3), 'mindegyiknek van izvilag-leirasa');
  ok(data && new Set(data.map(s => s.emoji)).size === 7, 'het kulonbozo emoji');

  // ── 1-3. a Pub kepernyoje ──
  console.log('\n===== A PUB LISTAJA =====');
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column';
    document.body.appendChild(root);
    // Profilok kellenek az ertekelo laphoz: a csillagok csak akkor elok, ha mar
    // tudjuk, KI ertekel. Ot profil = a valodi eset, ott a legmagasabb a lap.
    window.getProfiles = () => Promise.resolve([
      { id:'p1', name:'Bacsinszky Ádám', color:'#A78BFA' }, { id:'p2', name:'Bíró Bence', color:'#4FC2A0' },
      { id:'p3', name:'Kecskés Márk', color:'#6FA86F' },    { id:'p4', name:'Kiss Vivien', color:'#E8843C' },
      { id:'p5', name:'Makláry Sára', color:'#E86A9B' },
    ]);
    ReactDOM.createRoot(root).render(React.createElement(BarScreen, { go: () => {}, deepLink: null }));
  });
  await p.waitForTimeout(1800);

  const txt = () => p.evaluate(() => document.body.innerText);
  let t = await txt();
  ok(NAMES.every(n => t.includes(n)), 'mind a het shot kint van a listaban',
     NAMES.filter(n => !t.includes(n)).join(',') || 'mind');

  // a cimke-pirula pontosan egyszer szerepel
  const chips = await p.evaluate(t2 => [...document.querySelectorAll('button')]
    .filter(x => (x.innerText || '').trim().toLowerCase() === t2).length, TAG);
  ok(chips === 1, 'a cimke PONTOSAN egyszer szerepel a szuroben', chips);

  // ra kattintva csak ez a het marad
  const clicked = await p.evaluate(t2 => {
    const btn = [...document.querySelectorAll('button')]
      .find(x => (x.innerText || '').trim().toLowerCase() === t2);
    if (btn) btn.click();
    return !!btn;
  }, TAG);
  ok(clicked, 'a cimke-pirula kattinthato');
  await p.waitForTimeout(700);
  t = await txt();
  ok(NAMES.every(n => t.includes(n)), 'szures utan is mind a het latszik');
  ok(!/Barack Attack/.test(t) && !/Bogyóbomba/.test(t),
     'a cimke nelkuli DNR keveresek KIESNEK a szurt listabol');

  // ── 6. a reszletek lapja ──
  console.log('\n===== A RESZLETEK LAPJA =====');
  await p.evaluate(() => {
    const el = [...document.querySelectorAll('*')]
      .find(x => x.children.length === 0 && (x.innerText || '').trim() === 'Tropical Fusion');
    let n = el;
    for (let i = 0; i < 8 && n; i++) { if (n.onclick) { n.click(); return; } n = n.parentElement; }
    if (el) el.click();
  });
  await p.waitForTimeout(1000);
  t = await txt();
  ok(/295 ml[\s\S]*Finlandia vodka/.test(t) && /115 ml[\s\S]*szóda \/ citrom-lime/.test(t),
     'a hozzavalok 1 literes mennyisegekkel latszanak');
  ok(/25\s*adag/.test(t), 'az alap adagszam 25 (1 liter felesekbe töltve)');
  ok(t.includes(TAG), 'a cimke a RESZLETEK lapjan is kint van (nem csak a szuroben)');
  ok(/Egységes trópusi ízvilág/.test(t), 'az izvilag-leiras is latszik');

  // ── 7. az ertekelo lap: a fix also sav nem csuszhat a csillagokra ──
  // A reszletek „Szerkesztés / Értékelés" savja PORTALBA megy (a body-ba), tehat
  // a lapnal magasabban ult, es ra csuszott a csillag-sorra. A javitas nem
  // z-index: a sav a MOGOTTE levo laphoz tartozik, ezert `ratingFor` alatt
  // egyszeruen nem renderelodik.
  console.log('\n===== AZ ERTEKELO LAP =====');
  await p.evaluate(() => {
    const b2 = [...document.querySelectorAll('button')].find(x => /^Értékelés/.test((x.innerText || '').trim()));
    if (b2) b2.click();
  });
  await p.waitForTimeout(900);
  await p.evaluate(() => {
    const b3 = [...document.querySelectorAll('button')].find(x => /Bíró Bence/.test(x.innerText || ''));
    if (b3) b3.click();   // ertekelo kivalasztva → a csillagok elok lesznek
  });
  await p.waitForTimeout(500);
  const g = await p.evaluate(() => {
    const lbl = [...document.querySelectorAll('*')]
      .find(x => x.children.length === 0 && /HÁNY CSILLAGOT/i.test(x.innerText || ''));
    const row = lbl ? lbl.nextElementSibling : null;
    const r = row ? row.getBoundingClientRect() : null;
    let hit = null;
    if (r) {
      const el = document.elementFromPoint(Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2));
      hit = el ? (row.contains(el) || el === row) : false;
    }
    return { bottom: r ? Math.round(r.bottom) : null, vh: window.innerHeight,
             hit, bar: [...document.querySelectorAll('button')].filter(x => /Szerkesztés/.test(x.innerText || '')).length };
  });
  ok(g.bar === 0, 'az ertekelo lap alatt NEM latszik a „Szerkesztés" sav', g.bar);
  ok(g.bottom !== null && g.bottom <= g.vh, 'a csillag-sor a kepernyon belul van', g.bottom + ' / ' + g.vh);
  ok(g.hit === true, 'a csillagokra tenylegesen ra lehet koppintani (semmi nem takarja)');

  // ── 8. az ertekeles visszavonhato ──
  // A 0 csillag nem jo visszavonasra: az beleszamitana az atlagba. A mezot
  // tenylegesen ki kell venni a terkepbol — ezt nezi a store-ellenorzes.
  console.log('\n===== AZ ERTEKELES TORLESE =====');
  const delBtn = () => p.evaluate(() => [...document.querySelectorAll('button')]
    .some(x => /Értékelésem törlése/.test(x.innerText || '')));
  ok(!(await delBtn()), 'ertekeles NELKUL nincs torles gomb');

  // 4 csillag a kivalasztott ertekelotol
  await p.evaluate(() => {
    const lbl = [...document.querySelectorAll('*')]
      .find(x => x.children.length === 0 && /HÁNY CSILLAGOT/i.test(x.innerText || ''));
    const row = lbl ? lbl.nextElementSibling : null;
    // A csillagok <span>★</span>-ok, nem gombok — a 4. a negycsillagos ertekeles
    const st = row ? [...row.querySelectorAll('span')].filter(x => x.innerText.trim() === '★') : [];
    if (st[3]) st[3].dispatchEvent(new MouseEvent('click', { bubbles: true }));
  });
  await p.waitForTimeout(900);
  const stored = () => p.evaluate(() => {
    const doc = ((window.__fbStore || {})['config'] || {})['drinkRatings'] || {};
    return doc['fg_tropicalfusion'] || {};
  });
  let s1 = await stored();
  ok(Object.keys(s1).length === 1, 'az ertekeles lement a Firestore-ba', JSON.stringify(s1));
  t = await txt();
  ok(/A te értékelésed/.test(t), 'a reszleteknel megjelenik „A te értékelésed" sor');

  // ujranyitas → most mar „Ertekeles modositasa", es van torles gomb
  await p.evaluate(() => {
    const b2 = [...document.querySelectorAll('button')].find(x => /^Értékelés/.test((x.innerText || '').trim()));
    if (b2) b2.click();
  });
  await p.waitForTimeout(800);
  ok(await delBtn(), 'modositasnal MAR van „Értékelésem törlése" gomb');

  await p.evaluate(() => {
    const b4 = [...document.querySelectorAll('button')].find(x => /Értékelésem törlése/.test(x.innerText || ''));
    if (b4) b4.click();
  });
  await p.waitForTimeout(900);
  const s2 = await stored();
  ok(!('p2' in s2), 'a mezo TENYLEGESEN eltunt a terkepbol (nem 0, nem null)', JSON.stringify(s2));
  t = await txt();
  ok(!/A te értékelésed/.test(t), 'a reszletekbol is eltunt a sajat ertekeles');
  ok(!/Értékelés módosítása/.test(t), 'az also gomb ujra „Értékelés" (nem „módosítása")');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));

  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
