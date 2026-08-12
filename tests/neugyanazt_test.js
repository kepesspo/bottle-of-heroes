// v10.342 — „Ne ugyanazt!" — az új páros játék
//
// Ketten KÖZÖSEN játszanak: három körben egyszerre mondanak egy-egy szót a
// témára, úgy, hogy NE ugyanazt. Egyszer sem egyeztek → mindketten pont;
// ahányszor egyeztek, annyit isznak.
//
// ⚠️ AMIT A LEGFONTOSABB ŐRIZNI: a TÉMÁK SZŰKSÉGE. „Állatok"-nál két ember
// gyakorlatilag soha nem mond ugyanazt — mindig pont járna, és nem lenne tét.
// A 4. blokk ezért a témabankot méri: nincs benne tág gyűjtőfogalom, és
// mindegyik rövid, konkrét halmazt jelöl ki.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'a', name:'Sere',  color:'#E07A5F', points:0, drinks:0 },
            { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 }];

const mount = (p, gameIdx) => p.evaluate(({ pl, gameIdx }) => {
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  let root = document.getElementById('__p'); if (root) root.remove();
  root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto;padding:10px';
  document.body.appendChild(root);
  window.__res = null; window.__adv = null;
  ReactDOM.createRoot(root).render(React.createElement(NeUgyanaztGame, {
    gameIdx, challenger: pl[0], opponent: pl[1],
    onResult: r => { window.__res = r; }, onAdvance: (dm, pm) => { window.__adv = { dm, pm }; } }));
}, { pl: PL, gameIdx });

const txt = p => p.evaluate(() => (document.getElementById('__p').innerText || '').replace(/\s+/g, ' '));
const click = (p, re) => p.evaluate((re) => {
  const x = [...document.querySelectorAll('#__p button')].find(y => new RegExp(re).test((y.textContent || '').trim()));
  if (!x) return 'NINCS'; x.click(); return 'ok';
}, re);
// A 3-2-1 magatol pereg (900 ms/lepes), utana jon a ket itelo gomb.
const waitJudge = async (p) => {
  for (let i = 0; i < 40; i++) {
    if (await p.evaluate(() => [...document.querySelectorAll('#__p button')]
      .some(x => /Mást mondtunk/.test(x.textContent || '')))) return true;
    await p.waitForTimeout(200);
  }
  return false;
};
// Egy teljes meccs: `sames` = koronkent egyezett-e
const playMatch = async (p, sames) => {
  await click(p, 'Kezdjük');
  for (const same of sames) {
    if (!(await waitJudge(p))) return false;
    await click(p, same ? 'Ugyanazt' : 'Mást mondtunk');
    await p.waitForTimeout(200);
  }
  await p.waitForTimeout(400);
  return true;
};

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1000 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // ── 1. A BEVEZETO: a tema MEG REJTVE, a szabaly kint ──
  console.log('\n===== 1. A BEVEZETO =====');
  await mount(p, 0);
  await p.waitForTimeout(800);
  const t0 = await txt(p);
  ok(/Sere.*Kecsi.*együtt játszotok/i.test(t0), 'mindkét játékos neve ott van', t0.slice(0, 80));
  ok(/NE ugyanazt/i.test(t0), 'a cél ki van mondva');
  ok(/annyit isztok|annyi kortyot/i.test(t0), 'és a tét is', t0.slice(0, 200));
  const hidden = await p.evaluate(() => [...document.querySelectorAll('#__p div')]
    .some(d => /repeating-linear-gradient/.test(d.style.background || '')));
  ok(hidden, 'a téma a bevezetőben MÉG REJTVE van');

  // ── 2. NULLA EGYEZES → mindketten PONT ──
  console.log('\n===== 2. NULLA EGYEZES =====');
  ok(await playMatch(p, [false, false, false]), 'a három kör lement');
  let out = await p.evaluate(() => ({ res: window.__res, adv: window.__adv }));
  ok((out.res.winners || []).length === 2, 'mindkét játékos NYERTES', (out.res.winners||[]).map(x=>x.name).join(','));
  ok((out.res.losers || []).length === 0 && out.res.drinks === 0, 'senki nem iszik', JSON.stringify({ l:(out.res.losers||[]).length, d:out.res.drinks }));
  ok(out.adv.pm.a === 1 && out.adv.pm.b === 1, 'mindketten +1 pont', JSON.stringify(out.adv.pm));
  ok(Object.keys(out.adv.dm).length === 0, 'korty senkinek', JSON.stringify(out.adv.dm));

  // ── 3. AHANYSZOR EGYEZTEK, ANNYIT ISZNAK ──
  console.log('\n===== 3. KET EGYEZES =====');
  await mount(p, 1);
  await p.waitForTimeout(700);
  ok(await playMatch(p, [true, false, true]), 'a három kör lement');
  out = await p.evaluate(() => ({ res: window.__res, adv: window.__adv }));
  ok((out.res.losers || []).length === 2, 'mindkét játékos ISZIK', (out.res.losers||[]).map(x=>x.name).join(','));
  ok(out.res.drinks === 2, 'PONTOSAN annyi korty, ahányszor egyeztek', out.res.drinks);
  ok(out.adv.dm.a === 2 && out.adv.dm.b === 2, 'és a könyvelés is ennyi', JSON.stringify(out.adv.dm));
  ok(Object.keys(out.adv.pm).length === 0, 'pont senkinek', JSON.stringify(out.adv.pm));

  // mind a harom egyezes
  await mount(p, 2);
  await p.waitForTimeout(700);
  await playMatch(p, [true, true, true]);
  out = await p.evaluate(() => ({ res: window.__res, adv: window.__adv }));
  ok(out.res.drinks === 3 && out.adv.dm.a === 3, 'három egyezés → három korty', out.res.drinks);

  // ── 4. ⚠️ A TEMABANK: SZUK temak, kulonben nincs jatek ──
  console.log('\n===== 4. A TEMABANK =====');
  const th = await p.evaluate(() => ({
    list: NEUGYANAZT_THEMES, n: NEUGYANAZT_THEMES.length, rounds: NEUGYANAZT_ROUNDS,
  }));
  ok(th.n === 40, 'negyven téma', th.n);
  ok(th.rounds === 3, 'három kör', th.rounds);
  ok(new Set(th.list).size === th.n, 'nincs ismétlődés');
  // Tag gyujtofogalom nem lehet benne: azzal ket ember soha nem egyezne.
  const TAG = /^(Állatok?|Ételek?|Italok?|Sportok?|Országok?|Városok?|Szavak?|Filmek?|Zenék?|Színek?|Gyümölcsök?|Zöldségek?|Növények?|Tárgyak?)$/i;
  const broad = th.list.filter(x => TAG.test(x.trim()));
  ok(broad.length === 0, 'egyetlen tág gyűjtőfogalom sincs benne', broad.join(', ') || 'egy sincs');
  ok(th.list.every(x => x.length <= 26), 'mind rövid, a kártyán is kifér',
     th.list.filter(x => x.length > 26).join(' | ') || 'mind');

  // Egy meccs HAROM KULONBOZO temat kap.
  const trio = await p.evaluate(() => {
    const n = NEUGYANAZT_THEMES.length;
    const bad = [];
    for (let g = 0; g < 40; g++) {
      const t = [0,1,2].map(i => NEUGYANAZT_THEMES[(g * 3 + i) % n]);
      if (new Set(t).size !== 3) bad.push(g);
    }
    return bad;
  });
  ok(trio.length === 0, 'egy meccsen belül mind a három téma KÜLÖNBÖZŐ', trio.join(',') || 'mind');

  // ── 5. a jatek be van kotve ──
  console.log('\n===== 5. BEKOTES =====');
  const g = await p.evaluate(() => {
    const x = GAMES.find(y => y.id === 'neugyanazt');
    return x ? { cat: x.category, hasBanner: !!x.banner, emoji: x.emoji, stake: x.stake } : null;
  });
  ok(!!g, 'ott van a GAMES listában');
  ok(g && g.cat === 'Páros', 'PÁROS játék', g && g.cat);
  ok(g && g.hasBanner, 'van bannere (a gameorder_test ezt megköveteli)');
  ok(g && g.stake && g.stake[0] === 0 && g.stake[1] === 3,
     'a fejléc-korong 0–3 kortyot ígér — pontosan ennyi lehet', JSON.stringify(g && g.stake));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await p.close();
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
