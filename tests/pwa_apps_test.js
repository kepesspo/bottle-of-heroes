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
    if (!q) {
      // v10.137: a dokk egyetlen app-fiók (nem gomb) — minden app a lapon van
      const dock = await pp.evaluate(() => {
        const row = Array.from(document.querySelectorAll('div')).find(d => /DNR appok/.test((d.innerText || '')) && d.getAttribute('role') === 'button');
        if (!row) return null;
        const r = row.getBoundingClientRect();
        const icons = Array.from(row.querySelectorAll('img')).map(i => i.getAttribute('src'));
        return { text: row.innerText.replace(/\n/g, ' | '), h: Math.round(r.height), icons, tag: row.tagName };
      });
      ok('van egyetlen app-fiók sor', !!dock, JSON.stringify(dock));
      ok('a fiók NEM <button> (nem gomb-kinézet)', dock && dock.tag === 'DIV', dock && dock.tag);
      ok('mind az 5 app ikonja ott van egymáson', dock && dock.icons.length === 5, JSON.stringify(dock && dock.icons));
      ok('egy sor magas (<=64px)', dock && dock.h <= 64, dock && dock.h + 'px');
      ok('a digest sor élő infót mutat', dock && /Köv\. esemény|A Box most szól|Events · BOX/.test(dock.text), dock && dock.text);
      const tiles = await pp.evaluate(() => Array.from(document.querySelectorAll('button')).filter(b => /^(Events|Box|Pub|Több|Bingó|Liga)$/.test((b.innerText || '').trim().split('\n')[0])).length);
      ok('nincs tobb kulon app-csempe a fooldalon', tiles === 0, 'db=' + tiles);
      // fiók megnyitasa -> mind az 5 app
      await pp.evaluate(() => { const row = Array.from(document.querySelectorAll('div')).find(d => /DNR appok/.test(d.innerText || '') && d.getAttribute('role') === 'button'); if (row) row.click(); });
      await pp.waitForTimeout(700);
      const sheet = await pp.evaluate(() => document.body.innerText);
      ok('a lap "DNR appok" cimmel nyilik', /DNR appok/.test(sheet));
      for (const n of ['DNR Events', 'DNR BOX', 'DNR Pub', 'DNR Bingó', 'DNR Liga']) ok('a lapon ott: ' + n, sheet.includes(n));
      ok('a Liga sora a futo szezont mutatja', /Ranglista · S2 · Nyár/.test(sheet), (sheet.match(/Ranglista[^\n]*/) || ['NINCS'])[0]);
      await pp.screenshot({ path: __dirname + '/pwa_more_sheet.png', fullPage: true });
      await pp.evaluate(() => { const b = Array.from(document.querySelectorAll('button')).find(x => /DNR Bingó/.test(x.innerText || '')); if (b) b.click(); });
      await pp.waitForTimeout(1200);
      const after = await pp.evaluate(() => document.body.innerText);
      ok('a lapról el lehet jutni a Bingóba', /Bingó|Ki vagy/i.test(after) && !/DNR appok/.test(after), after.split('\n').slice(0, 3).join(' | '));
      // ujratoltes a fooldalra a szezon-badge teszthez
      await pp.goto(BASE, { waitUntil: 'domcontentloaded' });
      await pp.waitForTimeout(3200);
      // ── Szezon-badge a DNR GAMES alatt ──
      const badge = await pp.evaluate(() => {
        const b = Array.from(document.querySelectorAll('button')).find(x => /S2 · Ny[áÁ]r/i.test(x.innerText || ''));
        if (!b) return null;
        const r = b.getBoundingClientRect();
        const cs = getComputedStyle(b);
        const brand = Array.from(document.querySelectorAll('span')).find(x => /^DNR GAMES$/.test((x.innerText || '').trim()));
        const logo = document.querySelector('.home-brand svg, .home-brand img');
        const ring = b.querySelector('svg circle[stroke-dasharray]');
        return {
          text: (b.innerText || '').replace(/\n/g, ' | '),
          top: Math.round(r.top), h: Math.round(r.height), w: Math.round(r.width),
          ring: ring ? { dash: ring.getAttribute('stroke-dasharray'), color: ring.getAttribute('stroke') } : null,
          anim: cs.animationName,
          brandTop: brand ? Math.round(brand.getBoundingClientRect().top) : null,
          logoTop: logo ? Math.round(logo.getBoundingClientRect().top) : null,
        };
      });
      ok('van szezon-badge', !!badge, JSON.stringify(badge));
      ok('a szezon nevet mutatja', badge && /S2 · NYÁR|S2 · Nyár/i.test(badge.text), badge && badge.text);
      ok('kiirja a hatralevo napokat', badge && /\d+ nap|Ma zárul/i.test(badge.text), badge && badge.text);
      ok('a DNR GAMES ALATT van', badge && badge.brandTop != null && badge.top > badge.brandTop, `badge=${badge && badge.top} brand=${badge && badge.brandTop}`);
      ok('a logo FOLOTT van', badge && badge.logoTop != null && badge.top < badge.logoTop, `badge=${badge && badge.top} logo=${badge && badge.logoTop}`);
      ok('van arany haladás-gyűrű (részben töltött)', badge && badge.ring && /^[\d.]+ [\d.]+$/.test(badge.ring.dash) && parseFloat(badge.ring.dash) > 0 && parseFloat(badge.ring.dash) < parseFloat(badge.ring.dash.split(' ')[1]), JSON.stringify(badge && badge.ring));
      ok('bepattano animacio', badge && /seasonPop/.test(badge.anim), badge && badge.anim);
      ok('egy sor magas (<=52px)', badge && badge.h <= 52, badge && badge.h + 'px');
      ok('nem log ki (<=358px)', badge && badge.w <= 358, badge && badge.w + 'px');
      await pp.screenshot({ path: __dirname + '/pwa_home_dock.png', fullPage: true });

      // koppintasra a Liga SZEZON nezete nyilik
      await pp.evaluate(() => { const b = Array.from(document.querySelectorAll('button')).find(x => /S2 · Ny[áÁ]r/i.test(x.innerText || '')); if (b) b.click(); });
      await pp.waitForTimeout(1400);
      const seasonView = await pp.evaluate(() => {
        const on = Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === 'Szezon');
        return { text: document.body.innerText, active: on ? getComputedStyle(on).color : null };
      });
      ok('a badge a Liga szezon-nezetet nyitja', /Aktív · még \d+ nap/.test(seasonView.text) && /S2 · Nyár/.test(seasonView.text), seasonView.text.split('\n').slice(0, 6).join(' | '));
      await pp.screenshot({ path: __dirname + '/pwa_season_view.png', fullPage: true });
    }
    ok(`${q || '(alap)'} nincs JS hiba`, pp.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, pp.__errs.join(' | '));
    await pp.close();
  }

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
