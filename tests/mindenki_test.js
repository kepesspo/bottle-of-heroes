// v10.375 — Mindenki Iszik: FORRÓ KRUMPLI (push-your-luck)
//
// A régi passzív „az app kisorsol valakit, iszik egyet" megszűnt. Az új mechanika:
// egy kezdő + 1 kortyos krumpli; a holder MEGISSZA az aktuális mennyiséget (kör
// vége) vagy PASSZOLJA a kövinek +1 kortyval. Az utolsó játékosnál — mielőtt
// visszaérne a kezdőhöz — muszáj meginni. Max = létszám.
//
// Fogódzók:
//  1) a tét minden passzal +1 (nehéz szinten ×3 a KIJELZÉS, de a könyvelés raw×nehézség)
//  2) az utolsó holdernél NINCS „Passzolom" gomb (körbeért → forced)
//  3) a könyvelés a HOLDER-re megy, a helyes (skálázott) kortyszámmal
//  4) NYERS szám → a PlayScreen szoroz: nehéz szinten a 3. holder 3 raw = 9 korty
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const mount = (p, diff) => p.evaluate((diff) => {
  const r = document.getElementById('root'); if (r) r.style.display = 'none';
  const old = document.getElementById('__p'); if (old) old.remove();
  const root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:#EAF2FB';
  document.body.appendChild(root);
  function H() {
    const [ps, setPs] = React.useState([
      { id: 'a', name: 'Sere', color: '#E07A5F', points: 0, drinks: 0 },
      { id: 'b', name: 'Kecsi', color: '#4FC2A0', points: 0, drinks: 0 },
      { id: 'c', name: 'Vivi', color: '#A78BFA', points: 0, drinks: 0 },
      { id: 'd', name: 'Robi', color: '#60A5FA', points: 0, drinks: 0 }]);
    window.__players = ps;
    return React.createElement(PlayScreen, { go: () => {}, players: ps, setPlayers: setPs, selectedGames: ['mindenki'],
      roomCode: null, setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
      gameMeta: { modes: ['points', 'drinks'], difficulty: diff } });
  }
  ReactDOM.createRoot(root).render(React.createElement(H));
}, diff);

const potShown = p => p.evaluate(() => {
  const el = [...document.querySelectorAll('#__p div')].find(d => /A forró krumpli/i.test(d.textContent || '') && d.parentElement);
  // a nagy szám a "A forró krumpli" kártyán belül
  const card = el && el.closest('div');
  const m = (document.getElementById('__p').innerText || '').match(/A forró krumpli\s+🥔?\s*(\d+)/i);
  return m ? +m[1] : null;
});
const clickBtn = (p, re) => p.evaluate((reSrc) => {
  const re = new RegExp(reSrc);
  const b = [...document.querySelectorAll('#__p button')].find(x => re.test(x.textContent || ''));
  if (b) { b.click(); return true; } return false;
}, re.source);
const hasPass = p => p.evaluate(() => [...document.querySelectorAll('#__p button')].some(x => /Passzolom/.test(x.textContent || '')));
const stateOf = p => p.evaluate(() => (window.__players || []).map(x => ({ n: x.name, d: x.drinks, pt: x.points })));
const bannerTxt = p => p.evaluate(() => { const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250'); return el ? (el.innerText || '').replace(/\s+/g, ' ').trim() : ''; });

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. NEHÉZ, két passz után a 3. holder iszik: 3 raw × 3 = 9 korty ──
  console.log('\n===== 1. FORRÓ KRUMPLI — passz nő, holder iszik (nehéz, ×3) =====');
  {
    const p = await b.newPage({ viewport: { width: 402, height: 900 } });
    p.__errs = [];
    p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
    await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.addInitScript(stub);
    await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
    await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(3000);
    await mount(p, 'hard');
    await p.waitForTimeout(2200);

    ok(await potShown(p) === 3, 'induláskor a krumpli 1 raw × 3 = 3 korty', await potShown(p));
    ok(await hasPass(p), 'az első holdernél VAN „Passzolom" gomb');

    await clickBtn(p, /Passzolom/); await p.waitForTimeout(200);
    ok(await potShown(p) === 6, 'egy passz után 2 raw × 3 = 6 korty', await potShown(p));

    await clickBtn(p, /Passzolom/); await p.waitForTimeout(200);
    ok(await potShown(p) === 9, 'két passz után 3 raw × 3 = 9 korty', await potShown(p));
    ok(await hasPass(p), 'a 3. holder (4 főnél) még passzolhat');

    // a 3. holder iszik
    await clickBtn(p, /Megiszom/); await p.waitForTimeout(1400);
    const banner = await bannerTxt(p);
    // banner minimalize + Kövi
    await p.evaluate(() => { const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250'); if (el) el.click(); });
    await p.waitForTimeout(300);
    await clickBtn(p, /Kövi/i); await p.waitForTimeout(1600);
    const st = await stateOf(p);
    // startIdx = gameIdx(0) % 4 = 0 → Sere; +2 passz → holder = Vivi (index 2)
    const vivi = st.find(x => x.n === 'Vivi');
    ok(vivi && vivi.d === 9, '⚠️ a holder (Vivi) 3 raw × 3 = 9 kortyot kapott a könyvelésben', vivi && vivi.d);
    ok(st.filter(x => x.d > 0).length === 1, 'csak EGY ember ivott', st.filter(x => x.d > 0).map(x => x.n).join(','));
    ok(/9\s*KORTY/i.test(banner), 'a banner „9 KORTY" metrikát mutat', (banner.match(/\d+\s*KORTY/i) || ['nincs'])[0]);
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  // ── 2. KÖNNYŰ, végig passz → az utolsó holder FORCED (nincs passz), max = létszám ──
  console.log('\n===== 2. KÖRBEÉR — az utolsó holder muszáj iszik (könnyű, max=4) =====');
  {
    const p = await b.newPage({ viewport: { width: 402, height: 900 } });
    p.__errs = [];
    p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
    await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.addInitScript(stub);
    await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
    await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(3000);
    await mount(p, 'easy');
    await p.waitForTimeout(2200);

    // 3× passz → 4. (utolsó) holder
    for (let i = 0; i < 3; i++) { await clickBtn(p, /Passzolom/); await p.waitForTimeout(180); }
    ok(await potShown(p) === 4, 'a 4. holdernél a krumpli 4 korty (max = létszám)', await potShown(p));
    ok(!(await hasPass(p)), '⚠️ az utolsó holdernél NINCS „Passzolom" gomb (körbeért)');

    await clickBtn(p, /Megiszom/); await p.waitForTimeout(1400);
    await p.evaluate(() => { const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250'); if (el) el.click(); });
    await p.waitForTimeout(300);
    await clickBtn(p, /Kövi/i); await p.waitForTimeout(1600);
    const st = await stateOf(p);
    const robi = st.find(x => x.n === 'Robi'); // index 3, az utolsó
    ok(robi && robi.d === 4, 'a kényszerített utolsó holder (Robi) 4 kortyot ivott', robi && robi.d);
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
