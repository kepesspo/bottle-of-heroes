// v10.239 — Admin ▸ Rendszer ▸ Partik: egy parti visszavonása
//
// Miért lehet egyáltalán visszavonni: a statEvents / gameStatEvents pontosan
// azokat a deltákat tárolja, amiket a parti alatt hozzáadtunk a stats /
// game_stats összesítőkhöz. A visszavonás ugyanezeket vonja le, majd törli az
// eseményeket.
//
// Amit ellenőriz:
//   1. az események idővonalából annyi parti áll össze, amennyit vártunk
//      (a statEvents a parti VÉGÉN, a gameStatEvents menet közben keletkezik —
//      csak együtt adnak parti-ablakot)
//   2. a visszavonás PONTOSAN a parti deltáit vonja le az összesítőkből
//   3. a parti eseményei törlődnek
//   4. a MÁSIK parti érintetlen marad (se összesítő, se esemény)
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

const DAY = 86400000;

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

  // ── seed: két parti, 2 nap különbséggel ──
  // A régi (P1) és az új (P2). Mindkettőben ugyanaz a két profil játszik, hogy
  // kiderüljön: a visszavonás csak a saját deltáit vonja le.
  await p.evaluate(async (DAY) => {
    const db = firebase.firestore();
    const now = Date.now();
    const t1 = now - 3 * DAY;      // régi parti
    const t2 = now - 2 * 3600000;  // mai parti (2 órája)
    window.__t1 = t1; window.__t2 = t2;

    // profilok
    await db.collection('profiles').doc('a').set({ name: 'Alfa' });
    await db.collection('profiles').doc('b').set({ name: 'Beta' });

    // P1 — regi parti: Alfa 10 pont / 20 korty, Beta 4 pont / 30 korty
    await db.collection('gameStatEvents').doc('g1').set({ gameId: 'quiz', ts: t1, plays: 3 });
    await db.collection('statEvents').doc('s1a').set({ profileId: 'a', ts: t1 + 3600000, totalPoints: 10, totalDrinks: 20, totalSessions: 1 });
    await db.collection('statEvents').doc('s1b').set({ profileId: 'b', ts: t1 + 3600000, totalPoints: 4, totalDrinks: 30, totalSessions: 1 });

    // P2 — mai parti: Alfa 7 pont / 5 korty, Beta 2 pont / 9 korty
    await db.collection('gameStatEvents').doc('g2').set({ gameId: 'quiz', ts: t2, plays: 2, winnerProfileId: 'a' });
    await db.collection('statEvents').doc('s2a').set({ profileId: 'a', ts: t2 + 1800000, totalPoints: 7, totalDrinks: 5, totalSessions: 1 });
    await db.collection('statEvents').doc('s2b').set({ profileId: 'b', ts: t2 + 1800000, totalPoints: 2, totalDrinks: 9, totalSessions: 1 });

    // osszesitok: a ket parti osszege (ahogy a valosagban is felepult)
    await db.collection('stats').doc('a').set({ totalPoints: 17, totalDrinks: 25, totalSessions: 2, bestStreak: 6 });
    await db.collection('stats').doc('b').set({ totalPoints: 6, totalDrinks: 39, totalSessions: 2 });
    await db.collection('game_stats').doc('quiz').set({ plays: 5, winners: { a: 1 } });
  }, DAY);

  // ── AdminParties kozvetlenul ──
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;overflow:auto';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(AdminParties));
  });
  await p.waitForTimeout(1600);

  const cards = () => p.evaluate(() => [...document.querySelectorAll('#__p button')]
    .filter(x => /Visszavonás/.test(x.innerText || '')).length);
  ok(await cards() === 2, 'két partit ismert fel az idővonalból', String(await cards()));

  const chips = await p.evaluate(() => document.querySelector('#__p').innerText.replace(/\s+/g, ' '));
  ok(/Alfa · 7 pont · 5 korty/.test(chips), 'a mai parti bontása helyes (Alfa 7/5)', chips.slice(0, 200));

  // ── visszavonjuk a LEGFRISSEBB partit (a lista tetején) ──
  await p.evaluate(() => {
    const btn = [...document.querySelectorAll('#__p button')].find(x => /^Visszavonás$/.test((x.innerText || '').trim()));
    btn.click();
  });
  await p.waitForTimeout(300);
  await p.evaluate(() => {
    const btn = [...document.querySelectorAll('#__p button')].find(x => /Biztos\? Visszavonom/.test(x.innerText || ''));
    btn.click();
  });
  await p.waitForTimeout(1800);

  const after = await p.evaluate(() => {
    const s = window.__fbStore;
    return {
      statsA: s['stats'] && s['stats'].a,
      statsB: s['stats'] && s['stats'].b,
      quiz: s['game_stats'] && s['game_stats'].quiz,
      seIds: Object.keys(s['statEvents'] || {}).sort(),
      geIds: Object.keys(s['gameStatEvents'] || {}).sort(),
    };
  });

  ok(after.statsA.totalPoints === 10 && after.statsA.totalDrinks === 20 && after.statsA.totalSessions === 1,
     'Alfa összesítője pontosan a régi partira csökkent', JSON.stringify(after.statsA));
  ok(after.statsB.totalPoints === 4 && after.statsB.totalDrinks === 30 && after.statsB.totalSessions === 1,
     'Beta összesítője pontosan a régi partira csökkent', JSON.stringify(after.statsB));
  ok(after.statsA.bestStreak === 6, 'a rekord-értékhez nem nyúlt (nem is tudná visszaállítani)', String(after.statsA.bestStreak));
  ok(after.quiz.plays === 3, 'a játék-statisztika is a régi partira csökkent', JSON.stringify(after.quiz));
  ok((after.quiz.winners || {}).a === 0, 'a győzelem-számláló is csökkent', JSON.stringify(after.quiz.winners));
  ok(JSON.stringify(after.seIds) === JSON.stringify(['s1a', 's1b']), 'csak a mai parti stat-eseményei tűntek el', after.seIds.join(','));
  ok(JSON.stringify(after.geIds) === JSON.stringify(['g1']), 'csak a mai parti játék-eseményei tűntek el', after.geIds.join(','));

  await p.waitForTimeout(400);
  ok(await cards() === 1, 'a listában már csak a régi parti maradt', String(await cards()));
  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
