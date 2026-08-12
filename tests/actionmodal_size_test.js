// v10.344 — Az akció-modal nem nőhet a képernyő méretére
//
// A bejelentés: „ha a statisztika oldalon rányomok egy profilra, akkor túl
// nagyban jelenik meg". A kártya a képernyő tetejétől az aljáig ért.
//
// ⚠️ AZ OK: a közös `ActionModal` kártyájának nem volt magasság-korlátja és nem
// volt görgetése. Rövid modalnál (egy mondat + két gomb) ez sosem látszott, a
// `QuickStatsModal` viszont egy TELJES profil-statisztikát tesz bele — a kártya
// addig nőtt, amíg el nem fogyott a képernyő.
//
// A MÁSODIK, súlyosabb következmény: ami nem fért ki, az LEVÁGÓDOTT, és
// görgetni sem lehetett hozzá. Ezt méri a 2. blokk — a puszta „mekkora a
// kártya" mérés ezt nem fogná meg.
//
// A 4. blokk a kontroll: egy RÖVID modal nem változhat. Enélkül egy „mindent
// 620-ra vágok" regresszió is átmenne.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const VH = 860;

// A kartya: a 28 px sarok-sugaru, szeles doboz a fedo retegen belul.
const card = p => p.evaluate(() => {
  const c = [...document.querySelectorAll('#__p div')]
    .find(d => getComputedStyle(d).borderRadius === '28px' && d.getBoundingClientRect().width > 280);
  if (!c) return null;
  const r = c.getBoundingClientRect();
  const body = [...c.children].find(x => getComputedStyle(x).overflowY === 'auto');
  const btn = c.querySelector('button');
  const br = btn ? btn.getBoundingClientRect() : null;
  return {
    h: Math.round(r.height), top: Math.round(r.top), bottom: Math.round(r.bottom),
    scrollable: body ? body.scrollHeight > body.clientHeight + 2 : null,
    // a gomb a KARTYAN BELUL kell legyen — ez bizonyitja, hogy nem vagodott le
    btnInside: br ? (br.bottom <= r.bottom + 1 && br.top >= r.top) : null,
  };
});

const mount = (p, what) => p.evaluate((what) => {
  window.__fbStore['stats'] = { pr1: { totalDrinks:1031, totalPoints:186, totalSessions:403, totalWins:60, xp:10198 } };
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  let root = document.getElementById('__p'); if (root) root.remove();
  root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;background:var(--app-bg)';
  document.body.appendChild(root);
  const el = what === 'hosszu'
    ? React.createElement(QuickStatsModal, {
        profile: { id:'pr1', profileId:'pr1', name:'Szécsi Márk', color:'#5BA0DB' },
        badges: [], onClose: () => {} })
    : React.createElement(ActionModal, {
        onClose: () => {}, kicker: 'Rövid', onPrimary: () => {}, primaryLabel: 'Rendben' },
        'Egy mondat, semmi több.');
  ReactDOM.createRoot(root).render(el);
}, what);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: VH } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');localStorage.setItem('boh_theme','ice');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);

  // ── 1. A HOSSZU lap: kartya, nem kepernyo ──
  console.log('\n===== 1. A PROFIL-LAP MERETE =====');
  await mount(p, 'hosszu');
  await p.waitForTimeout(1800);
  const long = await card(p);
  ok(!!long, 'megvan a kártya', JSON.stringify(long));
  ok(long.h <= 620, 'a kártya legfeljebb 620 px', long.h + ' px');
  ok(long.top > 40 && long.bottom < VH - 40,
     'fent ÉS lent is látszik a háttér — kártyának néz ki, nem képernyőnek',
     'top=' + long.top + ' bottom=' + long.bottom + ' / ' + VH);

  // ── 2. ⚠️ A LENYEG: ami nem fer ki, az GORGETHETO (nem vagodik le) ──
  console.log('\n===== 2. A TARTALOM GORGETHETO =====');
  ok(long.scrollable === true, 'a hosszú tartalom görgethető a kártyán belül', long.scrollable);
  ok(long.btnInside === true, 'és a „Bezár" gomb a kártyán BELÜL van — nem vágódott le', long.btnInside);

  // ── 3. a fej es a gombsor nem zsugorodik ──
  console.log('\n===== 3. A FEJ ES A GOMBSOR HELYEN MARAD =====');
  const fixed = await p.evaluate(() => {
    const c = [...document.querySelectorAll('#__p div')]
      .find(d => getComputedStyle(d).borderRadius === '28px' && d.getBoundingClientRect().width > 280);
    const kids = [...c.children];
    return kids.map(k => ({ shrink: getComputedStyle(k).flexShrink, ov: getComputedStyle(k).overflowY }));
  });
  const bodyIdx = fixed.findIndex(k => k.ov === 'auto');
  ok(bodyIdx > 0, 'a görgő törzs nem az első elem (van fej fölötte)', bodyIdx);
  ok(fixed.filter((k, i) => i !== bodyIdx).every(k => k.shrink === '0'),
     'a törzsön KÍVÜL minden elem flexShrink:0', JSON.stringify(fixed.map(k => k.shrink)));

  // ── 4. KONTROLL: a rovid modal NEM valtozik ──
  // Enelkul egy „mindent 620-ra vagok" regresszio is atmenne.
  console.log('\n===== 4. KONTROLL — A ROVID MODAL =====');
  await mount(p, 'rovid');
  await p.waitForTimeout(900);
  const short = await card(p);
  ok(short.h < 300, 'a rövid modal a természetes magasságán marad', short.h + ' px');
  ok(short.scrollable === false, 'és nem görget', short.scrollable);
  ok(short.btnInside === true, 'a gombja is a helyén', short.btnInside);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
