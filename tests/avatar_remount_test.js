// v10.335 — ⚠️ Alkomponens a törzsben = minden rendereléskor ÚJRAMOUNT
//
// A bejelentés: „Tappernél ugrálnak az avatarok. Mindig ráfrissül."
//
// AZ OK (harmadszor ugyanez): ha egy alkomponens a szülő TÖRZSÉBEN van
// definiálva, minden újrarendereléskor ÚJ függvény-azonosságot kap. A React
// ezt MÁS komponens-típusnak látja: nem frissíti a meglévő fát, hanem leszedi
// és újramountolja — az avatar `<img>` pedig ezzel együtt újratöltődik.
//
// A Tappernél a visszaszámláló `setInterval` 40 MS-onként ketyeg, tehát
// másodpercenként 25-ször épült újra mindkét tábla.
//
// A FOGÓDZÓ NEM a geometria, hanem a DOM-CSOMÓPONT AZONOSSÁGA. A régi teszt
// (`tapper_press_test`) az avatar pozícióját mérte — az újramountolt kép
// UGYANOTT jelenik meg, tehát a geometria-ellenőrzés a hibás verzión is
// átment. Ezért itt megjelöljük a csomópontot egy saját tulajdonsággal, és
// azt nézzük, megvan-e még a ketyegés után: egy újramountolt `<img>` friss
// csomópont, a jelölés nélkül.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

// A jelolo: minden avatar-kepre raírunk egy sorszamot. Ha a fa ujramountolodik,
// az uj csomoponton nincs jelolo.
const mark = p => p.evaluate(() => {
  const imgs = [...document.querySelectorAll('#__p img')];
  imgs.forEach((x, i) => { x.__mark = 'm' + i; });
  return imgs.length;
});
const survived = p => p.evaluate(() => {
  const imgs = [...document.querySelectorAll('#__p img')];
  return { total: imgs.length, kept: imgs.filter(x => x.__mark).length };
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // ── 1. TAPPER: a visszaszamlalas alatt sem epulhet ujra a tabla ──
  console.log('\n===== 1. TAPPER — A VISSZASZAMLALAS ALATT =====');
  await p.evaluate(() => {
    const av = (typeof CHAR_AVATARS !== 'undefined' && CHAR_AVATARS) || [];
    const pl = [{ id:'a', name:'Sere', color:'#E07A5F', img: av[0] && av[0].img },
                { id:'b', name:'Kecsi', color:'#4FC2A0', img: av[1] && av[1].img }];
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(TapperGame, {
      gameIdx: 0, challenger: pl[0], opponent: pl[1], roomCode: null,
      onAdvance: () => {}, onResult: () => {} }));
  });
  await p.waitForTimeout(1400);
  const n0 = await mark(p);
  ok(n0 >= 2, 'megvan mindkét tábla profilképe', n0);

  // mindket tablat lenyomjuk -> elindul az 5 mp-es visszaszamlalas (40 ms-os
  // interval), tehat a szulo masodpercenkent ~25-szor rendereli ujra magat
  // A szintetikus PointerEventnek nincs valodi pointere, tehat a
  // `setPointerCapture` dobna — ugyanaz a fogas, mint a ledger_test-ben.
  await p.evaluate(() => { Element.prototype.setPointerCapture = function () {}; });
  const boxes = await p.evaluate(() => [...document.querySelectorAll('#__p img')]
    .map(x => { const r = x.getBoundingClientRect(); return { x: r.x + r.width/2, y: r.y + r.height/2 }; }));
  await p.evaluate((bs) => bs.forEach((b, i) => {
    const el = document.elementFromPoint(b.x, b.y);
    const tap = el && el.closest('div[style*="touch-action"]') || el;
    tap && tap.dispatchEvent(new PointerEvent('pointerdown', { bubbles:true, pointerId: 10 + i }));
  }), boxes);
  await p.waitForTimeout(1600);   // ~40 ujrarenderelesnyi ketyeges
  const counting = await p.evaluate(() => /^\d\.\d$/.test(
    ([...document.querySelectorAll('#__p span')].map(s => (s.textContent||'').trim())
      .find(t => /^\d\.\d$/.test(t)) || '')));
  ok(counting, 'a visszaszámláló tényleg ketyeg (a szülő újrarenderel)');
  const s1 = await survived(p);
  ok(s1.kept === s1.total && s1.total >= 2,
     'a profilkép DOM-csomópontja TÚLÉLTE a ketyegést — nincs újramount',
     s1.kept + ' / ' + s1.total);

  // ── 2. a forras: alkomponens NEM ulhet a torzsben, ha JSX-kent hasznaljuk ──
  // Ez a fogodzo az EGESZ osztalyt orzi, nem csak a Tappert. A kulonbseg nem a
  // definicio helye, hanem a HASZNALAT: a result-banner `Pile`/`Metric`/`Row`
  // szandekosan a renderen belul keletkezik, DE sima fuggvenykent hivjuk
  // (`Pile({...})`), tehat a React nem lat kulon tipust.
  console.log('\n===== 2. A FORRAS: TORZSBEN DEFINIALT JSX-KOMPONENSEK =====');
  const src = fs.readFileSync(ROOT + '/app.src.html', 'utf8');
  const lines = src.split('\n');
  const inBody = {};
  lines.forEach((l, i) => {
    const m = l.match(/^(\s+)(?:const|let|function)\s+([A-Z]\w*)\s*(?:=\s*(?:\([^)]*\)|\w+)\s*=>|=\s*function|\()/);
    if (m && m[1].length > 0) (inBody[m[2]] = inBody[m[2]] || []).push(i + 1);
  });
  const asJsx = Object.keys(inBody).filter(n => new RegExp('<' + n + '[\\s/>]').test(src));
  // Amelyik AVATART is rajzol, az a bejelentett hiba: az `<img>` ujratoltodik.
  const withAvatar = asJsx.filter(n => inBody[n].some(ln => {
    const body = lines.slice(ln - 1, ln + 70).join('\n');
    return /<img|PlayerAvatar/.test(body);
  }));
  console.log('    törzsben definiált + JSX:', asJsx.length, '· ebből avataros:', withAvatar.length);
  ok(!asJsx.includes('Btn'), 'a Tapper `Btn`-je kikerült a törzsből');
  ok(!withAvatar.includes('LargeCard'), 'a Kisebb/Nagyobb `LargeCard`-ja kikerült', withAvatar.join(','));
  ok(!withAvatar.includes('PlayerCard'), 'a Kő-papír `PlayerCard`-ja kikerült', withAvatar.join(','));
  ok(!withAvatar.includes('PlayerChip'), 'a Beerpong observer `PlayerChip`-je kikerült', withAvatar.join(','));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
