// Buli-könyvelés füstteszt
// -------------------------------------------------------------------------
// Minden játékot végigjátszik (generikus "kattints tovább" driverrel), és
// összeveti, amit az eredmény-banner (onResult) ígér azzal, amit a játék
// ténylegesen átad a buli állásának (onAdvance).
//
// A ma javított három hiba mind ebbe a családba tartozott:
//  - a győztes nem kapott pontot (Időpárbaj, Útvesztő)
//  - a Beer Pong eredménye eldobódott a lezárásnál
//
// Használat:  node ledger_test.js [jatekId ...]
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');

const PLAYERS = [
  { id:'a', name:'Anna', color:'#5BA0DB', profileId:'p_a', points:0, drinks:0 },
  { id:'b', name:'Bela', color:'#E07A5F', profileId:'p_b', points:0, drinks:0 },
  { id:'c', name:'Cili', color:'#81B29A', profileId:'p_c', points:0, drinks:0 },
  { id:'d', name:'Dani', color:'#F2CC8F', profileId:'p_d', points:0, drinks:0 },
];

// Gombfeliratok, amikkel egy játék előre halad. Sorrend = prioritás.
const ADVANCE_PATTERNS = [
  'nyert', 'Döntetlen', 'Kész', 'Mehet', 'Indul', 'Indít', 'Start', 'Kezd', 'Tovább',
  'Koppints', 'Most', 'Csenget', 'Nálam', 'Nálad',
  'Megnézem', 'Rendben', 'OK$', 'Vége', 'Befejez', 'Stop', 'Leállít',
  'Igen', 'Nem', 'Iszik', 'Elrontotta', 'Sikerült', 'Nem sikerült',
  'Következő', 'Dobás', 'Pörget', 'Húz', 'Felfed', 'Válasz',
];

async function playOne(browser, gameId) {
  const p = await browser.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(() => { try { localStorage.setItem('boh_onboarded','1'); } catch(e){} });
  await p.goto('file:///home/user/bottle-of-heroes/index.html', { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ gameId, players }) => {
    window.__adv = []; window.__res = [];
    const root = document.createElement('div'); root.id='__g';
    root.style.cssText = 'position:fixed;inset:0;overflow:auto;background:#F5D89B;z-index:99999;padding:8px';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(window.GameContent, {
      gameId, gameIdx: 0, players,
      challenger: players[0], opponent: players[1],
      roomCode: null,
      gameMeta: { modes:['points','drinks'], difficulty:'easy',
                  beerpongConfig:{ tournamentType:'se', matchMinutes:0, visszavago:false, maxCups:10, mode:'egyeni' } },
      onAdvance: (dm, pm, opts) => window.__adv.push({ dm: dm||{}, pm: pm||{}, opts: opts||null }),
      onResult:  (r) => { if (r) window.__res.push({
                    winners: (r.winners||[]).filter(Boolean).map(x=>x.id),
                    losers:  (r.losers ||[]).filter(Boolean).map(x=>x.id),
                    drinks: r.drinks ?? null, winNote: r.winNote || null, correct: r.correct ?? null }); },
      onUnready: ()=>{}, onLiveDrinkUpdate: ()=>{}, onSetHideFooter: ()=>{},
      onSetBuszSwitch: ()=>{}, onSetBpEnded: ()=>{}, onCommit: ()=>{},
    }));
  }, { gameId, players: PLAYERS });
  await p.waitForTimeout(900);

  // Generikus driver. Ha a képernyő szövege nem változik két kattintás után,
  // ráváltunk a rács-cellákra (Útvesztő csapdalerakás, Memória, Collect…).
  let clicks = 0, stuck = 0, lastText = '';
  for (let step = 0; step < 44; step++) {
    if (await p.evaluate(() => window.__adv.length > 0)) break;
    const did = await p.evaluate(({ pats, gridMode }) => {
      const root = document.getElementById('__g');
      const clickCells = () => {
        const cells = Array.from(root.querySelectorAll('div,button')).filter(el => {
          const r = el.getBoundingClientRect();
          return r.width >= 16 && r.width <= 80 && Math.abs(r.width - r.height) <= 8 && el.children.length <= 1;
        });
        if (!cells.length) return null;
        cells[Math.floor(Math.random() * cells.length)].click();
        return '#cella';
      };
      if (gridMode) { const c = clickCells(); if (c) return c; }
      const btns = Array.from(root.querySelectorAll('button, [role="button"], div[style*="cursor: pointer"]'))
        .filter(b => { const r = b.getBoundingClientRect(); return r.width > 8 && r.height > 8 && !b.disabled; });
      for (const pat of pats) {
        const rx = new RegExp(pat, 'i');
        const hit = btns.find(b => rx.test((b.innerText||'').trim()));
        if (hit) { hit.click(); return (hit.innerText||'').trim().slice(0,24); }
      }
      const names = ['Anna','Bela','Cili','Dani'];
      const nameHit = btns.find(b => names.includes((b.innerText||'').trim()));
      if (nameHit) { nameHit.click(); return '@' + (nameHit.innerText||'').trim(); }
      if (btns.length) { const t = btns[btns.length-1]; t.click(); return '·' + (t.innerText||'').trim().slice(0,20); }
      return clickCells();
    }, { pats: ADVANCE_PATTERNS, gridMode: stuck >= 2 });
    if (did) clicks++;
    await p.waitForTimeout(did ? 400 : 800);
    const now = await p.evaluate(() => document.getElementById('__g').innerText);
    if (now === lastText) stuck++; else { stuck = 0; lastText = now; }
    if (stuck > 14) break; // tényleg beragadt
  }
  await p.waitForTimeout(1200);

  const out = await p.evaluate(() => ({ adv: window.__adv, res: window.__res, text: document.getElementById('__g').innerText.slice(0,120) }));
  await p.close();
  return { ...out, clicks, errs };
}

// A banner (onResult) és a könyvelés (onAdvance) egyezésének ellenőrzése
function check(gameId, r) {
  const problems = [];
  if (!r.adv.length) return { status:'NEM_JATSZHATO', problems, note:`${r.clicks} kattintás után sem hívott onAdvance-t` };
  const pm = {}, dm = {};
  r.adv.forEach(a => {
    Object.entries(a.pm).forEach(([k,v]) => pm[k] = (pm[k]||0) + v);
    Object.entries(a.dm).forEach(([k,v]) => dm[k] = (dm[k]||0) + v);
  });
  const res = r.res.filter(x => x.winners.length || x.losers.length);
  res.forEach(x => {
    // győztest hirdet + pontot ígér -> kapjon is pontot
    const promisesPoint = x.winNote && /pont/i.test(x.winNote);
    if (x.winners.length && promisesPoint) {
      const missing = x.winners.filter(id => !(pm[id] > 0));
      if (missing.length) problems.push(`a banner "${x.winNote}"-ot ígér ${x.winners.join(',')}-nak, de a pontok: ${JSON.stringify(pm)}`);
    }
    // vesztest hirdet + kortyot ígér -> kapjon is kortyot
    if (x.losers.length && (x.drinks == null || x.drinks > 0)) {
      const missing = x.losers.filter(id => !(dm[id] > 0));
      if (missing.length) problems.push(`a banner ${x.losers.join(',')}-t iszásra ítéli, de a kortyok: ${JSON.stringify(dm)}`);
    }
  });
  Object.entries(pm).forEach(([k,v]) => { if (v < 0) problems.push(`negatív pont: ${k}=${v}`); });
  return { status: problems.length ? 'HIBA' : 'OK', problems, pm, dm, nRes: res.length };
}

(async () => {
  const only = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  // játéklista az appból
  const p0 = await browser.newPage({ viewport:{ width:390, height:844 } });
  await p0.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p0.addInitScript(stub);
  await p0.addInitScript(() => { try { localStorage.setItem('boh_onboarded','1'); } catch(e){} });
  await p0.goto('file:///home/user/bottle-of-heroes/index.html', { waitUntil:'domcontentloaded' });
  await p0.waitForTimeout(3500);
  let ids = await p0.evaluate(() => (window.GAMES||[]).map(g => g.id));
  await p0.close();
  if (only.length) ids = ids.filter(x => only.includes(x));
  console.log(`${ids.length} játék\n`);

  const buckets = { OK: [], HIBA: [], NEM_JATSZHATO: [], CRASH: [] };
  for (const id of ids) {
    let r, c;
    try { r = await playOne(browser, id); c = check(id, r); }
    catch (e) { buckets.CRASH.push([id, e.message]); console.log(`  ${id.padEnd(14)} CRASH ${e.message.slice(0,60)}`); continue; }
    if (r.errs.length) c.problems.push('konzolhiba: ' + r.errs[0].slice(0,70));
    if (r.errs.length && c.status === 'OK') c.status = 'HIBA';
    buckets[c.status].push([id, c]);
    const tag = c.status === 'OK' ? '✓' : c.status === 'HIBA' ? '✗' : '–';
    console.log(`  ${tag} ${id.padEnd(14)} ${c.status.padEnd(14)} pont=${JSON.stringify(c.pm||{})} korty=${JSON.stringify(c.dm||{})}${c.note ? '  ' + c.note : ''}`);
    c.problems.forEach(pr => console.log(`      → ${pr}`));
  }

  console.log(`\n==== ÖSSZEGZÉS ====`);
  console.log(`  OK:            ${buckets.OK.length}`);
  console.log(`  HIBA:          ${buckets.HIBA.length}  ${buckets.HIBA.map(x=>x[0]).join(', ')}`);
  console.log(`  nem játszható: ${buckets.NEM_JATSZHATO.length}  ${buckets.NEM_JATSZHATO.map(x=>x[0]).join(', ')}`);
  console.log(`  crash:         ${buckets.CRASH.length}  ${buckets.CRASH.map(x=>x[0]).join(', ')}`);
  await browser.close();
  process.exit(buckets.HIBA.length ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(2); });
