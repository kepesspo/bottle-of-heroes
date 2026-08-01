// v10.261 — Szerencsekerék: egy körben egyszer lehet pörgetni
//
// A HIBA: a gomb csak PÖRGÉS közben volt letiltva. Amint a kerék megállt, a
// felirat visszaváltott „PÖRGESS!"-re, és újra lehetett nyomni — az új pörgés
// pedig MÁSODSZOR is kiosztotta a kortyot.
//
// Amit ellenőriz:
//   1. pörgés közben nem indul újabb pörgés
//   2. az eredmény után a gomb LETILTVA marad, felirata „MEGVAN"
//   3. a gomb nyomkodása az eredmény után nem forgatja tovább a kereket
//   4. a korty PONTOSAN EGYSZER osztódik ki
//   5. új körben (gameIdx) újra lehet pörgetni
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

const btn = p => p.evaluate(() => {
  const root = document.getElementById('__wh');
  const b = [...root.querySelectorAll('button')].find(x => /PÖR|MEGVAN/i.test(x.innerText || ''));
  if (!b) return null;
  return { label: (b.innerText || '').replace(/\s+/g, ' ').trim(), disabled: b.disabled };
});

const press = async (p, times) => {
  for (let i = 0; i < (times || 1); i++) {
    await p.evaluate(() => {
      const root = document.getElementById('__wh');
      const b = [...root.querySelectorAll('button')].find(x => /PÖR|MEGVAN/i.test(x.innerText || ''));
      if (b) b.click();
    });
    await p.waitForTimeout(120);
  }
};

// A kerek elfordulasa — ebbol latszik, hogy egy ujabb kattintas inditott-e port.
const rot = p => p.evaluate(() => {
  const root = document.getElementById('__wh');
  const w = [...root.querySelectorAll('div')].find(d => d.style && /rotate/.test(d.style.transform || ''));
  return w ? w.style.transform : null;
});

const mount = (p, gameIdx) => p.evaluate(gi => {
  if (gi === 0) {
    window.__adv = []; window.__res = [];
    const old = document.getElementById('__wh'); if (old) old.remove();
    const root = document.createElement('div');
    root.id = '__wh';
    root.style.cssText = 'position:fixed;inset:0;background:#EAF2FB;padding:16px;overflow:auto;z-index:9';
    document.body.appendChild(root);
    window.__root = ReactDOM.createRoot(root);
  }
  window.__root.render(React.createElement(SzerencsekerékGame, {
    gameIdx: gi,
    players: [{ id:'a', name:'Sere', color:'#4FC2A0' }, { id:'b', name:'Luca', color:'#5BA0DB' },
              { id:'c', name:'Kecsi', color:'#EE9480' }],
    onAdvance: d => window.__adv.push(d),
    onResult: r => window.__res.push(r),
  }));
}, gameIdx);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await mount(p, 0);
  await p.waitForTimeout(500);

  console.log('\n===== 1. KIINDULÁS =====');
  const b0 = await btn(p);
  ok(b0 && !b0.disabled && /PÖRGESS/.test(b0.label), 'a gomb pörgethető', b0 && JSON.stringify(b0));

  console.log('\n===== 2. PÖRGÉS KÖZBEN =====');
  await press(p, 1);
  await p.waitForTimeout(400);
  const bSpin = await btn(p);
  const rotSpin = await rot(p);
  ok(bSpin && bSpin.disabled && /PÖRÖG/.test(bSpin.label), 'pörgés közben letiltva', bSpin && JSON.stringify(bSpin));
  await press(p, 5);
  ok(await rot(p) === rotSpin, 'a nyomkodás közben NEM indul újabb pörgés', rotSpin);

  console.log('\n===== 3. AZ EREDMÉNY UTÁN =====');
  await p.waitForTimeout(4600);   // SPIN_MS 3600 + 700 kiosztas + tartalek
  const bDone = await btn(p);
  const rotDone = await rot(p);
  ok(bDone && bDone.disabled, 'a gomb az eredmény után is LETILTVA marad', bDone && JSON.stringify(bDone));
  ok(bDone && /MEGVAN/.test(bDone.label), 'a felirata már nem „PÖRGESS!"', bDone && bDone.label);
  // v10.265: a "A KIVÁLASZTOTT" kartya kikerult — a kor vegen a result banner
  // mondja el ugyanezt. Itt mar csak azt orizzuk, hogy NEM jott vissza.
  const noCard = await p.evaluate(() =>
    !/A KIVÁLASZTOTT/i.test(document.getElementById('__wh').innerText || ''));
  ok(noCard, 'nincs külön „A kiválasztott" kártya (azt a result banner mondja el)');

  await press(p, 6);
  await p.waitForTimeout(600);
  ok(await rot(p) === rotDone, 'a gomb nyomkodása NEM forgatja tovább a kereket', rotDone);
  const stillDone = await p.evaluate(() => {
    const root = document.getElementById('__wh');
    const b = [...root.querySelectorAll('button')].find(x => /PÖR|MEGVAN/i.test(x.innerText || ''));
    return b ? b.disabled && /MEGVAN/.test(b.innerText) : false;
  });
  ok(stillDone, 'és a gomb továbbra is lezárt állapotban marad');

  console.log('\n===== 4. A KORTY EGYSZER MEGY KI =====');
  await p.waitForTimeout(4600);   // ha megis indult volna egy por, mostanra beerne
  const adv = await p.evaluate(() => window.__adv);
  const res = await p.evaluate(() => window.__res);
  ok(adv.length === 1, 'az onAdvance PONTOSAN egyszer futott', JSON.stringify(adv));
  ok(res.length === 1, 'az onResult PONTOSAN egyszer futott', JSON.stringify(res.map(r => r.playerName)));
  const total = Object.values(adv[0] || {}).reduce((s, v) => s + v, 0);
  ok(total === 1, 'összesen 1 korty ment ki', total + ' korty');

  console.log('\n===== 5. ÚJ KÖR =====');
  await mount(p, 1);
  await p.waitForTimeout(500);
  const b1 = await btn(p);
  ok(b1 && !b1.disabled && /PÖRGESS/.test(b1.label), 'új körben újra pörgethető', b1 && JSON.stringify(b1));
  const fresh = await p.evaluate(() =>
    !/A KIVÁLASZTOTT/i.test(document.getElementById('__wh').innerText || ''));
  ok(fresh, 'és az előző kiválasztott eltűnt');

  console.log('\n===== 6. A NEVEK NEM ÁLLNAK FEJJEL LEFELÉ =====');
  // Friss kor + porgetes, hogy a kerek TENYLEG el legyen forgatva.
  await mount(p, 2);
  await p.waitForTimeout(500);
  await press(p, 1);
  await p.waitForTimeout(4600);
  // Egy NEM forgatott elem befoglaloja pontosan akkora, mint a layout merete.
  // Ha a cimke dolne, a befoglaloja megnone — ezt merjuk, nem ranezesre.
  const labels = await p.evaluate(() => {
    const root = document.getElementById('__wh');
    const wheel = [...root.querySelectorAll('div')].find(d => d.style && /rotate\(/.test(d.style.transform || '') && d.style.width);
    const out = [];
    [...root.querySelectorAll('span')].forEach(sp => {
      const t = (sp.innerText || '').trim();
      if (!/^(Sere|Luca|Kecsi)$/.test(t)) return;
      const el = sp.parentElement;              // a cimke-doboz (avatar + nev)
      const r = el.getBoundingClientRect();
      out.push({ name: t, wDiff: Math.abs(r.width - el.offsetWidth), hDiff: Math.abs(r.height - el.offsetHeight),
                 tf: el.style.transform });
    });
    return { rot: wheel ? wheel.style.transform : '', out };
  });
  const deg = +(labels.rot.match(/rotate\(([-\d.]+)deg\)/) || [0, 0])[1];
  ok(Math.abs(deg % 360) > 5, 'a kerék tényleg el van forgatva', labels.rot);
  ok(labels.out.length === 3, 'megvan mind a három címke', JSON.stringify(labels.out.map(x => x.name)));
  ok(labels.out.every(x => /rotate\(/.test(x.tf)), 'a címkék ellenforgatnak', labels.out[0] && labels.out[0].tf);
  ok(labels.out.every(x => x.wDiff < 1.5 && x.hDiff < 1.5),
     'és ÁLLVA maradnak (a befoglalójuk nem nőtt meg)',
     JSON.stringify(labels.out.map(x => x.name + ': ' + x.wDiff.toFixed(1) + '/' + x.hDiff.toFixed(1))));

  console.log('\n===== 7. NEM GÖRGETHETŐ OLDALRA =====');
  // A kerek NEGYZET dobozat forgatjuk; az elforgatott befoglaloja √2-szer
  // szelesebb, amitol a tartalom oldalra gorgethetove valt (v10.264).
  const scroll = await p.evaluate(() => {
    const root = document.getElementById('__wh');
    const wrap = [...root.querySelectorAll('div')].find(d => d.style && d.style.overflow === 'hidden' && d.style.width === '100%');
    return { doc: document.documentElement.scrollWidth, client: document.documentElement.clientWidth,
             root: root.scrollWidth, rootClient: root.clientWidth, hasWrap: !!wrap };
  });
  ok(scroll.hasWrap, 'a kerék konténere levágja a túlnyúlást');
  ok(scroll.doc <= scroll.client, 'az oldal nem görgethető oldalra', scroll.doc + ' / ' + scroll.client);
  ok(scroll.root <= scroll.rootClient, 'a játék területe sem', scroll.root + ' / ' + scroll.rootClient);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
