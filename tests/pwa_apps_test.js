// v10.135 — DNR Bingó és DNR Liga mint önálló PWA (?screen=bingo / ?screen=liga)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const stub = fs.readFileSync('/home/user/bottle-of-heroes/tests/fbstub.js', 'utf8');
const ROOT = '/home/user/bottle-of-heroes';
const BASE = 'file://' + ROOT + '/index.html';

const DAY = 86400000, NOW = Date.now();
const S2 = { from: NOW - 10 * DAY, to: NOW + 10 * DAY };

const seed = `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  window.__fbStore['profiles'] = { p_a:{name:'Alfa',color:'#5BA0DB'}, p_b:{name:'Beta',color:'#E07A5F'} };
  window.__fbStore['stats'] = {
    p_a:{ totalPoints:640, totalDrinks:320, totalSessions:28, totalRounds:1200, totalWins:12 },
    p_b:{ totalPoints:300, totalDrinks:150, totalSessions:12, totalRounds:400, totalWins:4 },
  };
  window.__fbStore['game_stats'] = {};
  window.__fbStore['statEvents'] = {
    e1:{ profileId:'p_a', ts:${S2.from + DAY}, totalPoints:300, totalSessions:6, totalRounds:200, totalDrinks:100 },
  };
  window.__fbStore['gameStatEvents'] = {};
  window.__fbStore['seasons'] = { s2:{ name:'S2 · Nyár', from:${S2.from}, to:${S2.to} } };
`;

async function open(b, query) {
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed);
  await p.goto(BASE + query, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(400);
  p.__splash = await p.evaluate(() => {
    const t = document.getElementById('splash-title-wrap');
    const g = document.getElementById('splash-tagline');
    const l = document.getElementById('splash-logo');
    return { title: (t ? t.textContent : '').trim(), tag: (g ? g.textContent : '').trim(), logo: l ? l.getAttribute('src') : null };
  });
  await p.waitForTimeout(2900);
  p.__errs = errs;
  return p;
}

const head = (p) => p.evaluate(() => ({
  title: document.title,
  manifest: (document.querySelector('link[rel="manifest"]') || {}).getAttribute
    ? document.querySelector('link[rel="manifest"]').getAttribute('href') : null,
  appleIcon: (document.querySelector('link[rel="apple-touch-icon"]') || {}).getAttribute
    ? document.querySelector('link[rel="apple-touch-icon"]').getAttribute('href') : null,
  appleTitle: (document.querySelector('meta[name="apple-mobile-web-app-title"]') || {}).content || null,
  text: document.body.innerText,
  backBtns: Array.from(document.querySelectorAll('button')).filter(x => x.querySelector('svg path[d^="M15 18l-6-6"]')).length,
}));

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

  // ── Fájlok ──
  console.log('===== FAJLOK =====');
  for (const f of ['manifest-bingo.json', 'manifest-liga.json', 'assets/dnr_bingo_icon.png', 'assets/dnr_liga_icon.png']) {
    ok('letezik: ' + f, fs.existsSync(path.join(ROOT, f)));
  }
  for (const [f, name, url] of [['manifest-bingo.json', 'DNR Bingó', '?screen=bingo'], ['manifest-liga.json', 'DNR Liga', '?screen=liga']]) {
    const m = JSON.parse(fs.readFileSync(path.join(ROOT, f), 'utf8'));
    ok(f + ' neve helyes', m.name === name, m.name);
    ok(f + ' start_url a sajat kepernyore mutat', (m.start_url || '').endsWith(url), m.start_url);
    ok(f + ' standalone', m.display === 'standalone', m.display);
    ok(f + ' 3 ikonmeret', (m.icons || []).length === 3 && m.icons.every(i => fs.existsSync(path.join(ROOT, i.src))), JSON.stringify((m.icons||[]).map(i => i.sizes)));
  }

  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── DNR Bingó ──
  console.log('\n===== ?screen=bingo · DNR BINGO =====');
  const pb = await open(b, '?screen=bingo');
  const hb = await head(pb);
  ok('cim: DNR Bingó', hb.title === 'DNR Bingó', hb.title);
  ok('manifest-bingo.json toltodik', /manifest-bingo\.json/.test(hb.manifest || ''), hb.manifest);
  ok('sajat apple-touch-icon', /dnr_bingo_icon\.png/.test(hb.appleIcon || ''), hb.appleIcon);
  ok('iOS app-nev: DNR Bingó', hb.appleTitle === 'DNR Bingó', hb.appleTitle);
  ok('egybol a bingo kepernyon indul', /BINGÓ|Bingó|Ki vagy/i.test(hb.text) && !/Bottle of Heroes/i.test(hb.text), hb.text.split('\n').slice(0, 4).join(' | '));
  ok('NINCS vissza-gomb (onallo app)', hb.backBtns === 0, 'db=' + hb.backBtns);
  ok('nincs onboarding', !/Üdv a Bottle of Heroes/.test(hb.text));
  ok('sajat nyito-kepernyo (nem "Bottle of Heroes")', pb.__splash.title === 'DNR Bingó' && /dnr_bingo_icon/.test(pb.__splash.logo || ''), JSON.stringify(pb.__splash));
  await pb.screenshot({ path: __dirname + '/pwa_bingo.png', fullPage: true });
  ok('nincs JS hiba', pb.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, pb.__errs.join(' | '));
  await pb.close();

  // ── DNR Liga ──
  console.log('\n===== ?screen=liga · DNR LIGA =====');
  const pl = await open(b, '?screen=liga');
  const hl = await head(pl);
  ok('cim: DNR Liga', hl.title === 'DNR Liga', hl.title);
  ok('manifest-liga.json toltodik', /manifest-liga\.json/.test(hl.manifest || ''), hl.manifest);
  ok('sajat apple-touch-icon', /dnr_liga_icon\.png/.test(hl.appleIcon || ''), hl.appleIcon);
  ok('iOS app-nev: DNR Liga', hl.appleTitle === 'DNR Liga', hl.appleTitle);
  ok('a fejlecben DNR Liga all (nem "Statisztika")', /DNR Liga/.test(hl.text) && !/^Statisztika/m.test(hl.text), hl.text.split('\n').slice(0, 3).join(' | '));
  ok('a ranglista betoltott (Alfa 640)', /Alfa/.test(hl.text) && /640/.test(hl.text));
  ok('a szezon-kapcsolo is mukodik', /Összes/.test(hl.text) && /Szezon/.test(hl.text));
  ok('NINCS vissza-gomb (onallo app)', hl.backBtns === 0, 'db=' + hl.backBtns);
  ok('sajat nyito-kepernyo (nem "Bottle of Heroes")', pl.__splash.title === 'DNR Liga' && /dnr_liga_icon/.test(pl.__splash.logo || ''), JSON.stringify(pl.__splash));
  // szezon nezet elerheto az onallo appban is
  await pl.evaluate(() => { const x = Array.from(document.querySelectorAll('button')).find(y => y.textContent.trim() === 'Szezon'); if (x) x.click(); });
  await pl.waitForTimeout(900);
  const seasonTxt = await pl.evaluate(() => document.body.innerText);
  ok('szezon nezet mukodik az onallo appban', /S2 · Nyár/.test(seasonTxt) && /Aktív/.test(seasonTxt));
  await pl.screenshot({ path: __dirname + '/pwa_liga.png', fullPage: true });
  ok('nincs JS hiba', pl.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, pl.__errs.join(' | '));
  await pl.close();

  // ── A regi appok nem serultek ──
  console.log('\n===== REGRESSZIO: A MEGLEVO APPOK =====');
  for (const [q, title, man] of [
    ['', 'DNR Games', 'manifest.json'],
    ['?screen=bar', 'DNR Pub', 'manifest-bar.json'],
    ['?screen=dnrbox', 'DNR BOX', 'manifest-dnrbox.json'],
    ['?screen=events', 'DNR Events', 'manifest-events.json'],
  ]) {
    const pp = await open(b, q);
    const hh = await head(pp);
    ok(`${q || '(alap)'} → ${title}`, hh.title === title, hh.title);
    ok(`${q || '(alap)'} → ${man}`, (hh.manifest || '').split('?')[0] === man, hh.manifest);
    if (!q) ok('a fooldal a DNR dokkban mutatja a Bingót és a Ligát', /Bingó/.test(hh.text) && /Liga/.test(hh.text), (hh.text.match(/DNR · A többi app[\s\S]{0,120}/) || ['NINCS'])[0].replace(/\n/g, ' | '));
    if (!q) ok('az alap app nyito-kepernyoje valtozatlan', /BOTTLE OF HEROES/.test(pp.__splash.title.replace(/\s+/g, ' ')) || /Bottle/i.test(pp.__splash.title), JSON.stringify(pp.__splash.title.replace(/\s+/g, '')));
    ok(`${q || '(alap)'} nincs JS hiba`, pp.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, pp.__errs.join(' | '));
    if (!q) await pp.screenshot({ path: __dirname + '/pwa_home_dock.png', fullPage: true });
    await pp.close();
  }

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
