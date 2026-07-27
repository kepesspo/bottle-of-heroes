// v10.148 — Növekedés-panel (Admin > Rendszer > Növekedés)
//
// Itt a kockázat nem vizuális: ha a parti-klaszterezés vagy a visszatérés-számolás
// téved, akkor egy SZÁM hazudik, ami alapján termékdöntés születik. Ezért a
// metrikák kézzel ellenőrizhető, felépített naplón futnak.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';
const DAY = 86400000;

async function open(b, seed) {
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  p.__errs = errs;
  return p;
}

const baseSeed = `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  window.__fbStore['profiles'] = {};
  window.__fbStore['stats'] = {};
  window.__fbStore['game_stats'] = {};
  window.__fbStore['statEvents'] = {};
  window.__fbStore['gameStatEvents'] = {};
  window.__fbStore['seasons'] = {};
  window.__fbStore['config'] = {};
  window.__fbStore['usage'] = {};
`;

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── A metrika-matek, felepitett naplon ──────────────────────────────────
  console.log('===== METRIKAK =====');
  let p = await open(b, baseSeed);
  const r = await p.evaluate((DAY) => {
    const now = Date.now();
    // 4 parti:
    //  P1 (5 napja):  a,b,c   ── ez a felallas ketszer jatszott (P1 + P3)
    //  P2 (4 napja):  a,d
    //  P3 (2 napja):  a,b,c   ── ugyanaz a felallas, mint P1  → visszatero tarsasag
    //  P4 (50 napja): e       ── kiesik a 30 napos ablakbol
    const ev = [];
    const party = (daysAgo, ids) => ids.forEach((id, k) => ev.push({
      profileId: id, ts: now - daysAgo * DAY + k * 900, totalSessions: 1, totalPoints: 3, totalRounds: 8, totalDrinks: 2,
    }));
    party(5,  ['a','b','c']);
    party(4,  ['a','d']);
    party(2,  ['a','b','c']);
    party(50, ['e']);
    const games = [
      { gameId:'kopapir', ts: now - 5*DAY }, { gameId:'kopapir', ts: now - 2*DAY },
      { gameId:'rulett',  ts: now - 4*DAY },
    ];
    const usage = [];
    return window.growthMetrics(ev, games, usage);
  }, DAY);

  ok('4 partit ismer fel a naplobol', r.totalParties === 4, `${r.totalParties}`);
  ok('az utolso parti 2 napja volt', Math.round((Date.now() - r.lastPartyTs) / DAY) === 2, String(Math.round((Date.now() - r.lastPartyTs) / DAY)));
  ok('30 napon belul 3 parti', r.p30 === 3, `${r.p30}`);
  ok('kulon jatekosok 30 napon belul: a,b,c,d = 4', r.pl30 === 4, `${r.pl30}`);
  ok('osszes kulon jatekos: a,b,c,d,e = 5', r.profileIds === 5, `${r.profileIds}`);
  ok('3 kulon felallas volt (abc, ad, e)', r.rosters === 3, `${r.rosters}`);
  ok('1 tarsasag jatszott ketszer (abc)', r.returningRosters === 1, `${r.returningRosters}`);
  ok('3 jatekos jott vissza masik napon (a,b,c)', r.returningProfiles === 3, `${r.returningProfiles}`);
  ok('a 12 hetes idosor 12 elemu', r.weeks.length === 12, `${r.weeks.length}`);
  // mind a harom friss parti (5, 4 es 2 napja) az UTOLSO 7 napos ablakba esik
  ok('az utolso heti oszlop mind a 3 friss partit tartalmazza', r.weeks[11].parties === 3, JSON.stringify(r.weeks.slice(-2).map(w => w.parties)));
  // az 50 napos parti is belefer a 12 hetes ablakba — nem esik le a diagramrol
  ok('a 12 hetes ablak mind a 4 partit lefedi', r.weeks.reduce((a, w) => a + w.parties, 0) === 4, JSON.stringify(r.weeks.map(w => w.parties)));
  ok('pontosan ket hetben volt parti (3 friss + az 50 napos)', r.weeks.filter(w => w.parties > 0).length === 2, JSON.stringify(r.weeks.map(w => w.parties)));

  // ── Jatek-nepszeruseg ───────────────────────────────────────────────────
  ok('a legtobbet jatszott a Kő-papír-olló (2)', r.gameRows[0].id === 'kopapir' && r.gameRows[0].n === 2, JSON.stringify(r.gameRows.slice(0, 2)));
  ok('a soha nem futott jatekok szama = osszes − 2', r.neverPlayed.length === r.gameRows.length - 2, `${r.neverPlayed.length} / ${r.gameRows.length}`);

  // ── Egy parti sorai NE essenek szet kulon partikra ──────────────────────
  const split = await p.evaluate(() => {
    const now = Date.now();
    // 6 fos buli: a sorok egymas utan, de 30 masodpercen belul irodnak ki
    const ev = ['a','b','c','d','e','f'].map((id, k) => ({ profileId:id, ts: now - 3600000 + k * 5000, totalSessions:1, totalPoints:1 }));
    return window.growthMetrics(ev, [], []);
  });
  ok('egy 6 fos buli EGY partinak szamit', split.totalParties === 1, `${split.totalParties}`);
  ok('mind a 6 jatekos ugyanabban a partiban van', split.pl30 === 6, `${split.pl30}`);

  // ── Ket kulon nap NE olvadjon ossze ─────────────────────────────────────
  const twoDays = await p.evaluate((DAY) => {
    const now = Date.now();
    const ev = [
      { profileId:'a', ts: now - 2*DAY, totalSessions:1 },
      { profileId:'a', ts: now - 1*DAY, totalSessions:1 },
    ];
    return window.growthMetrics(ev, [], []);
  }, DAY);
  ok('ket kulon napi buli ket parti', twoDays.totalParties === 2, `${twoDays.totalParties}`);
  ok('ugyanaz az egy jatekos visszaterokent szamit', twoDays.returningProfiles === 1, `${twoDays.returningProfiles}`);

  // ── Ures naplo: ne omoljon ossze, es ne hazudjon ────────────────────────
  const empty = await p.evaluate(() => window.growthMetrics([], [], []));
  ok('ures naplon 0 parti', empty.totalParties === 0);
  ok('ures naplon nincs "utolso parti"', empty.lastPartyTs === null);
  ok('ures naplon 0 visszatero tarsasag', empty.returningRosters === 0 && empty.rosters === 0);
  await p.close();

  // ── App-megnyitas naplozasa ─────────────────────────────────────────────
  console.log('\n===== APP-MEGNYITAS NAPLO =====');
  p = await open(b, baseSeed);
  await p.waitForTimeout(2000);   // a logAppOpen 4 mp-cel keslelteti magat
  const usage = await p.evaluate(() => window.__fbStore['usage']);
  const day = new Date().toISOString().slice(0, 10);
  ok('a mai napra keszult usage doksi', !!(usage && usage[day]), JSON.stringify(Object.keys(usage || {})));
  ok('a "games" app megnyitasa szamlalodott', (usage[day] || {}).open_games === 1, JSON.stringify(usage[day]));
  ok('a keszulek bekerult a devices map-be', Object.keys((usage[day] || {}).devices || {}).length === 1, JSON.stringify((usage[day] || {}).devices));

  // masodik megnyitas ugyanarrol a keszulekrol: a szamlalo no, a keszulek NEM duplazodik
  await p.evaluate(() => window.logAppOpen('games'));
  await p.evaluate(() => window.logAppOpen('bar'));
  await p.waitForTimeout(400);
  const usage2 = await p.evaluate(() => window.__fbStore['usage']);
  ok('masodik megnyitas: open_games = 2', (usage2[day] || {}).open_games === 2, JSON.stringify(usage2[day]));
  ok('masik app kulon szamlalon: open_bar = 1', (usage2[day] || {}).open_bar === 1, JSON.stringify(usage2[day]));
  ok('a devices map NEM nott (ugyanaz a keszulek)', Object.keys((usage2[day] || {}).devices || {}).length === 1, JSON.stringify((usage2[day] || {}).devices));
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.close();

  // ── A panel kirajzolodik ────────────────────────────────────────────────
  console.log('\n===== A PANEL =====');
  const now = Date.now();
  const seSeed = {};
  const addParty = (i, daysAgo, ids) => ids.forEach((id, k) => {
    seSeed['e' + i + '_' + k] = { profileId: id, ts: now - daysAgo * DAY + k * 900, totalSessions: 1, totalPoints: 4, totalRounds: 9, totalDrinks: 3 };
  });
  addParty(1, 5, ['a', 'b', 'c']); addParty(2, 4, ['a', 'd']); addParty(3, 2, ['a', 'b', 'c']);
  p = await open(b, baseSeed + `
    window.__fbStore['statEvents'] = ${JSON.stringify(seSeed)};
    window.__fbStore['gameStatEvents'] = { g1:{gameId:'kopapir',ts:${now - 5 * DAY}}, g2:{gameId:'rulett',ts:${now - 2 * DAY}} };
  `);
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__gr';
    root.style.cssText = 'width:390px;box-sizing:border-box;padding:12px;background:' + ((window._T && window._T.bg) || '#EFC77A');
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(window.AdminGrowth));
  });
  await p.waitForTimeout(1400);
  const t = await p.evaluate(() => document.getElementById('__gr').innerText.replace(/\n/g, ' | '));
  ok('kiirja, hany napja volt az utolso parti', /AZ UTOLSÓ PARTI \| 2 \| napja/i.test(t), (t.match(/AZ UTOLSÓ PARTI[^|]*\|[^|]*\|[^|]*/i) || ['?'])[0]);
  ok('kiirja az osszes partit es jatekost', /3 lezárt buli · 4 külön játékos/.test(t), (t.match(/Összesen[^|]*/) || ['?'])[0]);
  // ebben a szettben 2 kulon felallas van (abc, ad), es ebbol egy jatszott ketszer
  ok('a visszatero tarsasag 1 / 2', /VISSZATÉRÉS/i.test(t) && /1 \/ 2/.test(t), (t.match(/VISSZATÉRÉS[\s\S]{0,60}/i) || ['?'])[0].replace(/\n/g, ' | '));
  ok('a visszatero jatekos 3 / 4', /3 \/ 4/.test(t), (t.match(/\d \/ \d/g) || []).join(' '));
  ok('a jatekok blokk 2 / 45-ot mutat', /2 \/ 45játszottak legalább egyszer/.test(t), (t.match(/JÁTÉKOK[\s\S]{0,50}/i) || ['?'])[0].replace(/\n/g, ' | '));
  ok('kiirja, hany jatek nem futott meg sosem', /43 még sosem futott/.test(t), (t.match(/Mind a[^|]*/) || ['?'])[0]);
  ok('app-megnyitasnal ures allapot latszik', /Még nincs adat/.test(t), (t.match(/APP-MEGNYITÁS[\s\S]{0,80}/i) || ['?'])[0].replace(/\n/g, ' | '));
  const wide = await p.evaluate(() => {
    const el = document.getElementById('__gr');
    return { scroll: el.scrollWidth, client: el.clientWidth };
  });
  ok('nem log ki vizszintesen', wide.scroll <= wide.client + 1, JSON.stringify(wide));

  // A kartyak NE erjenek ki a keperyo szeleig — ugyanaz a 16px, mint a tobbi admin fulon
  const pad = await p.evaluate(() => {
    const root = document.getElementById('__gr');
    const wrap = root.firstElementChild;                    // az AdminGrowth kulso doboza
    const cards = Array.from(wrap.children).filter(c => c.getBoundingClientRect().width > 100);
    const rw = wrap.getBoundingClientRect();
    const lefts = cards.map(c => Math.round(c.getBoundingClientRect().left - rw.left));
    const rights = cards.map(c => Math.round(rw.right - c.getBoundingClientRect().right));
    return { n: cards.length, left: Math.min(...lefts), right: Math.min(...rights) };
  });
  ok('minden kartya bal oldalt 16px-re all a szelotol', pad.left === 16, JSON.stringify(pad));
  ok('es jobb oldalt is 16px-re', pad.right === 16, JSON.stringify(pad));
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.screenshot({ path: __dirname + '/growth_panel.png', fullPage: true });
  await p.close();

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
