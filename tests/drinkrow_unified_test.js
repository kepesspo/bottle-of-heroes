// v10.291 — a KÖZÖS korty-sor három felületen: Kategória, Én még soha, Lóverseny.
// Nem csak képet csinál: méri, hogy a sor tényleg 48 px MINDHÁROM helyen, és
// hogy a Lóverseny chipje nem tolja szét a sort.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const OUT = __dirname;
const stub = fs.readFileSync(path.join(ROOT, 'tests/fbstub.js'), 'utf8');

let fail = 0;
const ok = (c, n, x) => { console.log((c ? '  OK  ' : '  HIBA') + '   ' + n + (x !== undefined ? '  → ' + x : '')); if (!c) fail++; };

async function mount(p, gameId, n) {
  await p.evaluate(({ gameId, n }) => {
    const old = document.getElementById('__p'); if (old) old.remove();
    [...document.body.children].forEach(c => { if (c.id !== '__p') c.style.display = 'none'; });
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const nev = ['Sere','Kecsi','Luca','Tóth','Márk','Dani'].slice(0, n);
    function H() {
      const [players, setPlayers] = React.useState(nev.map((x,i)=>({ id:'p'+i, name:x, color:'#5BA0DB', points:0, drinks:0 })));
      window.__players = players;
      return React.createElement(PlayScreen, { go:()=>{}, players, setPlayers, selectedGames:[gameId],
        roomCode:null, setGameMeta:()=>{}, setScoreHistory:()=>{}, setLastGameRound:()=>{},
        gameMeta:{ modes:['points'], difficulty:'easy' } });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  }, { gameId, n });
  await p.waitForTimeout(2600);
  await p.evaluate(() => { const pop=[...document.querySelectorAll('div')].find(d=>d.style&&d.style.zIndex==='9998'); if(pop) pop.click(); });
  await p.waitForTimeout(600);
}

// Minden olyan sor magassaga, amelyben van jatekos-nev ES avatar.
const sorMeret = p => p.evaluate(() => {
  const R = document.getElementById('__p');
  const nevek = ['Sere','Kecsi','Luca','Tóth','Márk','Dani'];
  const out = [];
  // A sor: 14 px lekerekitesu doboz, amiben PONTOSAN egy jatekosnev all.
  // (Az avatar betus, ezert a sor szovege „S Sere" — nem startsWith.)
  [...R.querySelectorAll('div')].forEach(d => {
    if (!d.style || d.style.borderRadius !== '14px') return;
    const t = (d.innerText || '').replace(/\s+/g, ' ').trim();
    const talalt = nevek.filter(n => new RegExp('\\b' + n + '\\b').test(t));
    if (talalt.length === 1) out.push({ nev: talalt[0], h: Math.round(d.getBoundingClientRect().height) });
  });
  return out;
});

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await browser.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);

  console.log('\n===== KATEGÓRIA (pick változat) =====');
  await mount(p, 'kategoria', 6);
  await p.evaluate(() => {
    const R = document.getElementById('__p');
    const sor = [...R.querySelectorAll('div')].find(d => d.style && d.style.borderRadius === '14px' && /\bTóth\b/.test(d.innerText||''));
    if (sor) sor.click();
  });
  await p.waitForTimeout(400);
  let m = await sorMeret(p);
  ok(m.length >= 6, 'hat sor kirajzolódott', m.length + ' sor');
  ok(m.every(r => r.h === 48), 'minden sor pontosan 48 px', [...new Set(m.map(r=>r.h))].join('/') + ' px');
  const pipa = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const sor = [...R.querySelectorAll('div')].find(d => d.style && d.style.borderRadius === '14px' && /\bTóth\b/.test(d.innerText||''));
    return sor ? sor.querySelectorAll('svg').length : 0;
  });
  ok(pipa >= 1, 'a kiválasztott soron ott a pipa-ikon (SVG, nem ✓ karakter)', pipa + ' svg');
  ok(await p.evaluate(() => !/[✓✕]/.test(document.getElementById('__p').innerText||'')),
     'sehol nincs unicode pipa/kereszt a képernyőn');
  await p.screenshot({ path: path.join(OUT, 'row_kategoria.png') });

  console.log('\n===== ÉN MÉG SOHA (stepper változat) =====');
  await mount(p, 'sohanem', 6);
  await p.evaluate(() => {
    const b = document.querySelector('#__p button[aria-label="Egy korttyal több"]');
    if (b) b.click();
  });
  await p.waitForTimeout(400);
  m = await sorMeret(p);
  ok(m.length >= 5, 'sorok kirajzolódtak', m.length + ' sor');
  ok(m.every(r => r.h === 48), 'minden sor pontosan 48 px', [...new Set(m.map(r=>r.h))].join('/') + ' px');
  ok(await p.evaluate(() => document.querySelectorAll('#__p button[aria-label="Egy korttyal több"]').length > 0),
     'a + gomb aria-label-lel elérhető (ikon, nem szöveg)');
  await p.screenshot({ path: path.join(OUT, 'row_sohanem.png') });

  console.log('\n===== LÓVERSENY (chip + stepper) =====');
  await mount(p, 'loverseny', 6);
  const HORSES = ['Gyorslábú Géza','Csülök','Remegő Rezső','Pálinka Pista'];
  for (let i = 0; i < 6; i++) {
    await p.evaluate((h) => {
      const b = [...document.querySelectorAll('#__p button')].find(x => (x.innerText||'').includes(h));
      if (b) b.click();
    }, HORSES[i % 4]);
    await p.waitForTimeout(150);
    await p.evaluate(() => {
      const b = [...document.querySelectorAll('#__p button')].find(x => /Következő|Rajt/.test(x.innerText||'') && !x.disabled);
      if (b) b.click();
    });
    await p.waitForTimeout(300);
  }
  // megvarjuk a futam veget
  for (let i = 0; i < 60; i++) {
    if (await p.evaluate(() => /nyert!|Mindenki veszített/.test(document.getElementById('__p').innerText||''))) break;
    await p.waitForTimeout(600);
  }
  await p.waitForTimeout(700);
  m = await sorMeret(p);
  ok(m.length >= 5, 'az eredmény-sorok kirajzolódtak', m.length + ' sor');
  ok(m.length > 0 && m.every(r => r.h === 48),
     'a chip ELLENÉRE is 48 px minden sor (nem tört két sorba)', [...new Set(m.map(r=>r.h))].join('/') + ' px');
  const tul = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const rossz = [];
    [...R.querySelectorAll('div')].forEach(d => {
      if (d.style && d.style.borderRadius === '14px' && /\b(Sere|Kecsi|Luca|Tóth|Márk|Dani)\b/.test(d.innerText||'')) {
        if (d.scrollWidth > d.clientWidth + 1) rossz.push((d.innerText||'').replace(/\s+/g,' ').trim().slice(0,20));
      }
    });
    return rossz;
  });
  ok(tul.length === 0, 'egyik sor tartalma sem lóg ki vízszintesen', tul.join(', ') || 'nincs túlnyúlás');
  await p.screenshot({ path: path.join(OUT, 'row_loverseny.png') });

  ok(errs.length === 0, 'nincs JS hiba', errs.slice(0,3).join(' | '));
  console.log(fail ? `\n❌ ${fail} HIBA` : '\n✅ MINDEN ELLENORZES RENDBEN');
  await browser.close();
  process.exit(fail ? 1 : 0);
})();
