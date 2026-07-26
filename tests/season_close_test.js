// v10.142 — Szezonzáró: egyszer felugró összefoglaló + győztes trófea a listában
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

const DAY = 86400000, NOW = Date.now();
// S1: 40 napja lezárult (RÉGI — nem szabad felugrania)
// S2: 3 napja lezárult (FRISS — ennek kell feljönnie)  · S3: most fut
const S1 = { from: NOW - 70 * DAY, to: NOW - 40 * DAY };
const S2 = { from: NOW - 25 * DAY, to: NOW - 3 * DAY };
const S3 = { from: NOW - 1 * DAY,  to: NOW + 20 * DAY };

const seed = (seasons, cfg) => `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  window.__fbStore['profiles'] = {
    p_a:{name:'Alfa',color:'#5BA0DB'}, p_b:{name:'Beta',color:'#E07A5F'},
    p_c:{name:'Gamma',color:'#81B29A'}, p_d:{name:'Delta',color:'#F2CC8F'},
  };
  window.__fbStore['stats'] = {
    p_a:{ totalPoints:900, totalSessions:30, totalRounds:900, totalWins:10 },
    p_b:{ totalPoints:500, totalSessions:20, totalRounds:400, totalWins:5 },
    p_c:{ totalPoints:300, totalSessions:10, totalRounds:200, totalWins:2 },
    p_d:{ totalPoints:100, totalSessions:5,  totalRounds:80,  totalWins:0 },
  };
  window.__fbStore['game_stats'] = {};
  window.__fbStore['gameStatEvents'] = {};
  window.__fbStore['statEvents'] = {
    // S1 — Alfa nyeri
    a1:{ profileId:'p_a', ts:${S1.from + DAY}, totalPoints:400, totalSessions:5, totalDrinks:50, totalRounds:100 },
    a2:{ profileId:'p_b', ts:${S1.from + 2*DAY}, totalPoints:100, totalSessions:2, totalDrinks:20, totalRounds:40 },
    // S2 — Beta nyeri 320-260-200-ra; a legtöbb kortyot Delta itta, a legtöbb partit Gamma játszotta
    b1:{ profileId:'p_b', ts:${S2.from + DAY},   totalPoints:320, totalSessions:4, totalDrinks:40,  totalRounds:150 },
    b2:{ profileId:'p_a', ts:${S2.from + 2*DAY}, totalPoints:260, totalSessions:3, totalDrinks:30,  totalRounds:120 },
    b3:{ profileId:'p_c', ts:${S2.from + 3*DAY}, totalPoints:200, totalSessions:9, totalDrinks:60,  totalRounds:300 },
    b4:{ profileId:'p_d', ts:${S2.from + 4*DAY}, totalPoints:10,  totalSessions:1, totalDrinks:200, totalRounds:20 },
    // szezonokon KÍVÜL — nem számíthat bele
    x1:{ profileId:'p_d', ts:${S2.to + DAY}, totalPoints:9999, totalSessions:9, totalDrinks:9999, totalRounds:9999 },
  };
  window.__fbStore['seasons'] = ${JSON.stringify(seasons)};
  window.__fbStore['config'] = ${JSON.stringify(cfg || {})};
`;

const ALL = { s1:{ name:'S1 · Tavasz', from:S1.from, to:S1.to },
              s2:{ name:'S2 · Nyár',   from:S2.from, to:S2.to },
              s3:{ name:'S3 · Ősz',    from:S3.from, to:S3.to } };

async function home(b, seasons, storage, cfg) {
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed(seasons, cfg));
  if (storage) await p.addInitScript(`try { ${storage} } catch(e){}`);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);
  p.__errs = errs;
  return p;
}
const sheetText = (p) => p.evaluate(() => {
  const d = Array.from(document.querySelectorAll('div')).find(x => /SZEZON VÉGE/i.test(x.innerText || '') && x.style.borderRadius === '28px');
  return d ? d.innerText.replace(/\n/g, ' | ') : null;
});

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── seasonStandings / seasonWinsOf tiszta fuggvenyek ──
  console.log('===== SZEZON-SEGEDEK =====');
  let p = await home(b, ALL);
  const eng = await p.evaluate(({ s1, s2 }) => {
    const evs = Object.values(window.__fbStore['statEvents']);
    const profs = Object.keys(window.__fbStore['profiles']).map(id => ({ id, ...window.__fbStore['profiles'][id] }));
    const seasons = Object.keys(window.__fbStore['seasons']).map(id => ({ id, ...window.__fbStore['seasons'][id] }));
    return {
      s2: window.seasonStandings(evs, s2, profs).map(x => ({ id:x.id, pts:x.pts, drinks:x.drinks, sessions:x.sessions })),
      s1: window.seasonStandings(evs, s1, profs).map(x => ({ id:x.id, pts:x.pts })),
      winsA: window.seasonWinsOf('p_a', seasons, evs, profs).map(x => x.name),
      winsB: window.seasonWinsOf('p_b', seasons, evs, profs).map(x => x.name),
      winsC: window.seasonWinsOf('p_c', seasons, evs, profs).map(x => x.name),
    };
  }, { s1: { from: S1.from, to: S1.to }, s2: { from: S2.from, to: S2.to } });
  ok('S2 allasa pont szerint rendezve', JSON.stringify(eng.s2.map(x => x.id)) === '["p_b","p_a","p_c","p_d"]', JSON.stringify(eng.s2.map(x => x.id + ':' + x.pts)));
  ok('a szezonon kivuli 9999 pont NEM szamit bele', !eng.s2.some(x => x.pts > 1000) && !eng.s1.some(x => x.pts > 1000), JSON.stringify(eng.s2.map(x => x.pts)));
  ok('S1-et Alfa nyerte', eng.s1[0] && eng.s1[0].id === 'p_a', JSON.stringify(eng.s1));
  ok('csak a LEZARULT szezonok szamitanak gyozelemnek', JSON.stringify(eng.winsA) === '["S1 · Tavasz"]' && JSON.stringify(eng.winsB) === '["S2 · Nyár"]', `A=${JSON.stringify(eng.winsA)} B=${JSON.stringify(eng.winsB)}`);
  ok('aki nem nyert, annak nincs gyozelme', eng.winsC.length === 0, JSON.stringify(eng.winsC));

  // ── A szezonzaro felugrik ──
  console.log('\n===== SZEZONZARO FELUGRIK =====');
  const txt = await sheetText(p);
  ok('felugrott a szezonzaro', !!txt, txt);
  ok('a FRISSEN lezarult szezont mutatja (S2), nem a regit (S1)', txt && /S2 · Nyár/.test(txt) && !/S1 · Tavasz/.test(txt), txt);
  ok('a gyoztes Beta, 320 ponttal', txt && /SZEZON MVP \| Beta \| 320/.test(txt), txt);
  ok('a dobogo 2. es 3. helye is kint van (Alfa, Gamma)', txt && /Alfa \| 260/.test(txt) && /Gamma \| 200/.test(txt), txt);
  ok('mellekcim: legtobb korty = Delta (200)', txt && /Legtöbb korty \| Delta \| 200 korty/i.test(txt), txt);
  ok('mellekcim: legtobb parti = Gamma (9)', txt && /Legtöbb parti \| Gamma \| 9 parti/i.test(txt), txt);
  ok('kiirja, hogy mar fut a kovetkezo (S3)', txt && /Már fut a következő/.test(txt) && /S3 · Ősz/.test(txt), txt);
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.screenshot({ path: __dirname + '/season_close.png', fullPage: true });

  // ── Bezaras utan nem jon vissza ──
  const key = await p.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === 'Bezár');
    if (btn) btn.click();
    return null;
  });
  await p.waitForTimeout(600);
  ok('bezarhato', (await sheetText(p)) === null);
  await p.close();

  console.log('\n===== MODOK =====');
  // 'always' (alap): ujratoltes utan ismet feljon, akkor is, ha mar lattuk
  p = await home(b, ALL, "localStorage.setItem('boh_season_closed_s2','1');");
  ok('alapbol MINDEN inditasnal feljon (a regi "latott" jelzes ellenere is)', (await sheetText(p)) !== null);
  // fooldalra visszalepes NEM hozza elo ujra
  await p.evaluate(() => { const btn = Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === 'Bezár'); if (btn) btn.click(); });
  await p.waitForTimeout(500);
  await p.evaluate(() => { const c = Array.from(document.querySelectorAll('button')).find(b2 => b2.querySelector('svg line[x1="18"][y1="20"]')); if (c) c.click(); });
  await p.waitForTimeout(1200);
  await p.evaluate(() => { const b2 = Array.from(document.querySelectorAll('button')).find(x => x.querySelector('svg path[d^="M15 18l-6-6"]')); if (b2) b2.click(); });
  await p.waitForTimeout(1400);
  ok('a fooldalra visszalepes NEM hozza elo ujra', (await sheetText(p)) === null, 'ugyanaz az app-inditas');
  await p.close();
  // ujratoltes = uj app-inditas -> ismet feljon
  p = await home(b, ALL);
  ok('ujratoltes utan ismet feljon', (await sheetText(p)) !== null);
  await p.close();

  p = await home(b, ALL, "localStorage.setItem('boh_season_closed_s2','1');", { homeConfig:{ seasonCloseMode:'once' } });
  ok('"once" modban a mar latott szezon NEM ugrik fel', (await sheetText(p)) === null);
  await p.close();

  p = await home(b, ALL, null, { homeConfig:{ seasonCloseMode:'once' } });
  ok('"once" modban eloszor feljon', (await sheetText(p)) !== null);
  await p.evaluate(() => { const btn = Array.from(document.querySelectorAll('button')).find(x => x.textContent.trim() === 'Bezár'); if (btn) btn.click(); });
  await p.waitForTimeout(500);
  ok('"once" modban a bezaras elmentodik', (await p.evaluate(() => localStorage.getItem('boh_season_closed_s2'))) === '1');
  await p.close();

  p = await home(b, ALL, null, { homeConfig:{ seasonCloseMode:'off' } });
  ok('"off" modban SOHA nem ugrik fel', (await sheetText(p)) === null);
  await p.close();

  p = await home(b, { s1: ALL.s1 });   // csak a 40 napja lezarult
  ok('2 hetnel regebbi szezonzaro NEM ugrik fel', (await sheetText(p)) === null);
  await p.close();

  p = await home(b, { s3: ALL.s3 });   // csak a most futo
  ok('futo szezonnal NEM ugrik fel', (await sheetText(p)) === null);
  ok('viszont a szezon-badge latszik', await p.evaluate(() => /S3 · Ősz/i.test(document.body.innerText)));
  await p.close();

  // ── "Végeredmény" gomb -> Liga, EPPEN AZON a szezonon ──
  console.log('\n===== VEGEREDMENY GOMB =====');
  p = await home(b, ALL);
  await p.evaluate(() => { const btn = Array.from(document.querySelectorAll('button')).find(x => /Végeredmény/.test(x.textContent)); if (btn) btn.click(); });
  await p.waitForTimeout(1600);
  const league = await p.evaluate(() => document.body.innerText);
  ok('a Liga szezon-nezete nyilt meg', /Összes/.test(league) && /Lezárult/.test(league), league.split('\n').slice(0, 6).join(' | '));
  ok('EPPEN az S2 szezont mutatja (nem az alapertelmezettet)', /S2 · Nyár/.test((league.match(/S2 · Nyár[\s\S]{0,40}/) || [''])[0]) && /Lezárult/.test(league), (league.match(/S2 · Nyár[\s\S]{0,60}/) || ['NINCS'])[0].replace(/\n/g, ' | '));
  ok('a szezonzaro bezarult', (await sheetText(p)) === null);
  await p.screenshot({ path: __dirname + '/season_close_league.png', fullPage: true });
  await p.close();

  // ── Trofea a statisztika-listaban ──
  console.log('\n===== TROFEA A LISTABAN =====');
  p = await home(b, ALL, "localStorage.setItem('boh_season_closed_s2','1');");
  await p.evaluate(() => { const c = Array.from(document.querySelectorAll('button')).find(b2 => b2.querySelector('svg line[x1="18"][y1="20"]')); if (c) c.click(); });
  await p.waitForTimeout(1500);
  const rows = await p.evaluate(() => {
    const out = {};
    ['Alfa', 'Beta', 'Gamma', 'Delta'].forEach(n => {
      const el = Array.from(document.querySelectorAll('span')).find(d => d.children.length === 0 && d.textContent.trim() === n);
      const card = el && el.closest('div[style*="cursor"]');
      if (!card) return;
      const chip = Array.from(card.querySelectorAll('span')).find(x => x.getAttribute('title') && /megnyert szezon/.test(x.getAttribute('title')));
      out[n] = chip ? chip.getAttribute('title') : null;
    });
    return out;
  });
  ok('Alfanak van trofeaja (S1)', rows.Alfa === '1 megnyert szezon', JSON.stringify(rows));
  ok('Betanak van trofeaja (S2)', rows.Beta === '1 megnyert szezon', JSON.stringify(rows));
  ok('Gammanak NINCS', rows.Gamma === null || rows.Gamma === undefined, JSON.stringify(rows));
  ok('Deltanak NINCS', rows.Delta === null || rows.Delta === undefined, JSON.stringify(rows));
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.screenshot({ path: __dirname + '/season_close_rows.png', fullPage: true });
  await p.close();

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
