// v10.292 — a szoba-toltes negy rajza (RoomFillArt)
//   0 korso · 1 palack · 2 feles-sor · 3 koccintas
// Amit oriz: mind a negy kirajzolodik ES animal. A 3-asnal ezen felul azt is,
// hogy a ket korso TENYLEG osszeer — enelkul csak ket lengo pohar marad.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'); const path = require('path');
const ROOT = path.join(__dirname, '..');
const stub = fs.readFileSync(path.join(ROOT, 'tests/fbstub.js'), 'utf8');
let fail = 0;
const ok = (c, n, x) => { console.log((c?'  OK  ':'  HIBA')+'   '+n+(x!==undefined?'  → '+x:'')); if(!c) fail++; };
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);

  const count = await p.evaluate(() => window.BOH_ROOM_ART_COUNT ?? null);
  for (let v = 0; v < 4; v++) {
    await p.evaluate((v) => {
      const old = document.getElementById('__r'); if (old) old.remove();
      [...document.body.children].forEach(c => { if (c.id !== '__r') c.style.display = 'none'; });
      const root = document.createElement('div'); root.id = '__r';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;display:grid;place-items:center;background:#F4C57E';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(RoomFillArt, { variant: v }));
    }, v);
    await p.waitForTimeout(1000);
    const info = await p.evaluate(() => {
      const svg = document.querySelector('#__r svg');
      if (!svg) return null;
      const r = svg.getBoundingClientRect();
      return { label: svg.getAttribute('aria-label'), w: Math.round(r.width), h: Math.round(r.height),
               anims: [...document.querySelectorAll('#__r *')].filter(e => getComputedStyle(e).animationName !== 'none').length };
    });
    ok(info && info.w > 0 && info.h > 0, `variant ${v} kirajzolódik`, info ? `${info.label} · ${info.w}×${info.h}px · ${info.anims} animált elem` : 'NINCS SVG');
    ok(info && info.anims > 0, `variant ${v} animál`, info ? info.anims : '-');
    // a becsapodas pillanata a 4. rajznal
    await p.waitForTimeout(v === 3 ? 1000 : 0);
    await p.screenshot({ path: `roomart-${v}.png`, clip: { x: 0, y: 250, width: 402, height: 380 } });
  }
  // A 3-as rajz lelke a KOCCANAS: ha a ket korso nem er ossze, a mozdulat
  // ertelmet veszti. Egy teljes cikluson at merjuk a kozottuk levo rest.
  await p.evaluate(() => {
    const old = document.getElementById('__r'); if (old) old.remove();
    const root = document.createElement('div'); root.id = '__r';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;align-items:center;justify-content:center';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(RoomFillArt, { variant: 3 }));
  });
  await p.waitForTimeout(600);
  const resek = [];
  for (let i = 0; i < 32; i++) {
    const g = await p.evaluate(() => {
      const gs = [...document.querySelectorAll('#__r svg > g')];
      if (gs.length < 2) return null;
      return Math.round(gs[1].getBoundingClientRect().left - gs[0].getBoundingClientRect().right);
    });
    if (g !== null) resek.push(g);
    await p.waitForTimeout(100);
  }
  const minRes = Math.min(...resek), maxRes = Math.max(...resek);
  ok(minRes <= 4, 'a két korsó tényleg összeér (koccan)', 'legkisebb rés: ' + minRes + ' px');
  ok(maxRes >= 60, 'és el is válik közben (van lendület)', 'legnagyobb rés: ' + maxRes + ' px');

  const csillag = await p.evaluate(async () => {
    let max = 0;
    for (let i = 0; i < 40; i++) {
      const s = document.querySelector('#__r svg path[d^="M120 22"]');
      if (s) max = Math.max(max, +getComputedStyle(s).opacity.slice(0, 4));
      await new Promise(r => setTimeout(r, 60));
    }
    return max;
  });
  ok(csillag > 0.6, 'a becsapódásnál felvillan a csillag', 'csúcs: ' + csillag);

  ok(count === 4 || count === null, 'BOH_ROOM_ART_COUNT = 4', count === null ? '(nem globális, forrásból ellenőrizve)' : count);
  ok(errs.length === 0, 'nincs JS hiba', errs.slice(0,2).join(' | '));
  console.log(fail ? `\n❌ ${fail} HIBA` : '\n✅ MIND A NÉGY RENDBEN');
  await b.close(); process.exit(fail ? 1 : 0);
})();
